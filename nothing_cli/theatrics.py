"""pretty printing utilities for not"""
from pathlib import Path
from textwrap import indent
from typing import Any, Dict, Iterator, List, Tuple

from slugify import slugify
import typer

from .config import GlobalConfig
from .constants import (
    CWD_DOT_NOTHING_DIR,
    HOME_DOT_NOTHING_DIR,
    DirectoryChoicesForListCommand,
)
from .localization import polyglot as glot
from .filesystem import (
    glob_each_extension,
    deserialize_task_spec_file,
    task_spec_file_metadata,
    task_spec_location,
    task_spec_names_by_parent_dir_name,
    task_spec_object_metadata,
)
from .models import Step, TaskSpec


config = GlobalConfig()


def marquis(title, description):
    """A display of the title + description that

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     Looks Like This

        'With a description in quotes'
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    border_length = max(len(title), len(description)) + 8
    border = "~" * border_length

    typer.echo(border)
    typer.echo()
    typer.echo(f" {title} ")
    typer.echo(f"    '{description}' ")
    typer.echo()
    typer.echo(border)
    typer.echo()


def interactive_walkthrough(task_spec: TaskSpec) -> None:
    """Interactively walk through a task spec"""

    marquis(task_spec.title, task_spec.description)

    context_dict = {}

    if task_spec.context:
        for item in task_spec.context:
            context_value = typer.prompt(item.prompt)
            context_dict[item.var_name] = context_value

    typer.echo()
    for step in task_spec.steps:
        run_step(step, context_dict)

    typer.echo(config.completion_message)


def run_step(step: Step, context: Dict):
    """Run just one Step in a TaskSpec"""
    typer.echo(f"{config.step_prefix} {step.number}:")

    try:
        typer.echo(step.prompt.format(**context) + "\n")
    except KeyError:
        typer.echo(step.prompt + "\n")

    input(glot["nag"])
    typer.echo()


def multiprompt(*prompts: Tuple[str, Dict]) -> Iterator[Any]:
    """Allows the caller to receive the values from a series of prompts
    in the order they were passed. A "prompt" here is a tuple containing an
    echo-able (usually a string), dictionary of any kwargs to pass to typer.prompt."""

    for prompt, prompt_kwargs in prompts:
        value = ask(prompt, **prompt_kwargs)

        yield value


def prompt_for_new_args(
    name=None,
    default_extension=None,
    default_destination=None,
    expert=None,
    edit_after_write=None,
) -> Iterator[Any]:
    """Prompt for all arguments needed to perform `not do`"""

    title = ask(glot["new_title_prompt"])
    name = slugify(title) if name is None else name

    prompts = (
        (glot["new_description_prompt"], {}),
        (glot["new_name_prompt"], {"default": name}),
        (glot["new_extension_prompt"], {"default": default_extension}),
        (
            glot["new_destination_prompt"],
            {"default": default_destination, "type": Path},
        ),
        (glot["new_extra_config_prompt"], {"default": expert, "type": bool}),
        (glot["new_open_editor_prompt"], {"default": edit_after_write, "type": bool}),
    )

    return (title, *multiprompt(*prompts))


def prompt_for_copy_args(
    default_title=None,
    default_destination=None,
    default_extension=None,
    edit_after_write=None,
) -> Iterator[Any]:
    """Prompt for all arguments needed to perform `not copy`"""

    prompts = (
        (glot["edit_name_prompt"], {}),
        (glot["edit_title_prompt"], {"default": default_title, "type": str}),
        (
            glot["edit_destination_prompt"],
            {"default": default_destination, "type": Path},
        ),
        (glot["edit_extension_prompt"], {"default": default_extension, "type": str}),
        (glot["edit_open_editor_prompt"], {"default": edit_after_write, "type": bool}),
    )

    return multiprompt(*prompts)


# TODO this should be in filesystem
def _collect_fancy_list_input(
    showing_from_dir: DirectoryChoicesForListCommand,
) -> Dict[str, Dict[str, str]]:
    """Utility for show_fancy_list().

    Returns a dict with a key each for cwd and home.
    The values are dicts where the keys are human-friendly paths
    and the values are lists of Task Spec names."""

    show_both: bool = showing_from_dir is DirectoryChoicesForListCommand.both
    show_home: bool = showing_from_dir is DirectoryChoicesForListCommand.home
    show_cwd: bool = showing_from_dir is DirectoryChoicesForListCommand.cwd

    names_by_dir = {}

    if show_home or show_both:
        task_specs_in_home_dot_nothing_dir: Iterator[Path] = glob_each_extension(
            "*", HOME_DOT_NOTHING_DIR, recurse=True
        )

        names_by_dir["home"] = task_spec_names_by_parent_dir_name(
            task_specs_in_home_dot_nothing_dir, base_dir="home"
        )

    if show_cwd or show_both:
        task_specs_in_cwd_dot_nothing_dir: Iterator[Path] = glob_each_extension(
            "*", CWD_DOT_NOTHING_DIR, recurse=True
        )

        names_by_dir["cwd"] = task_spec_names_by_parent_dir_name(
            task_specs_in_cwd_dot_nothing_dir, base_dir="cwd"
        )

    return names_by_dir


def show_fancy_list(showing_from_dir: DirectoryChoicesForListCommand):
    """Show a pretty output of the task spec files contained in the specified dir."""

    task_spec_names_by_directory: Dict = _collect_fancy_list_input(showing_from_dir)

    for base_dir, subdir_dict in task_spec_names_by_directory.items():
        header = typer.style(
            f"[ {glot['GLOBAL'] if base_dir == 'home' else glot['LOCAL']} ]\n",
            typer.colors.BRIGHT_BLUE,
        )
        typer.echo(header)

        for dir_name, task_spec_list in subdir_dict.items():
            subdir_header = typer.style(
                indent(f"{dir_name}/", "  "), fg=typer.colors.CYAN
            )
            typer.echo(subdir_header)

            for i, name in enumerate(task_spec_list):
                typer.echo(indent(name, "    "))
                if i == len(task_spec_list) - 1:
                    typer.echo()


def confirm_overwrite(task_spec_name) -> bool:
    """Prompt y/n when user is attempting to create a Task Spec with the same
    name as an existing one"""

    existence_warning = typer.style(
        glot.localized("overwrite_warn", {"name": task_spec_name}),
        fg=typer.colors.YELLOW,
    )

    return typer.confirm(existence_warning, abort=True)


def confirm_drop(task_spec_name) -> bool:
    """Prompt y/n when user is about to delete a Task Spec file"""

    drop_is_destructive_warning = typer.style(
        glot.localized("drop_warn", {"name": task_spec_name}), fg=typer.colors.YELLOW
    )

    return typer.confirm(drop_is_destructive_warning, abort=True)


def success(message) -> None:
    """Echo the message with a stylish interjection above it"""

    stylish_interjection = typer.style(
        glot["stylish_interjection"], fg=typer.colors.GREEN
    )
    typer.echo(stylish_interjection)
    typer.echo(message)


def ask(question, **prompt_kwargs) -> Any:
    """Prompt the user with a question"""

    styled_question = typer.style(question, fg=typer.colors.BRIGHT_BLACK)
    answer = typer.prompt(styled_question, **prompt_kwargs)

    return answer


# TODO: raise typer.Abort() when called
def warn_missing_file(name):
    """A generic warning when a Task Spec with the specified name does not exist"""

    message = typer.style(
        glot.localized("missing_file_warn", {"name": name}), fg=typer.colors.YELLOW
    )
    typer.echo(message)


def justified_with_colons(*strings) -> List[str]:
    """For use when making lists like so:

    Item       :   yep
    Another    :   sure

    Will use the longest word's len + 4 for the width."""
    width = len(max(strings, key=len)) + 4

    return [string.ljust(width, " ") + ": " for string in strings]


def show_dossier(task_spec_name):
    """A pretty-printed overview of some Task Spec metadata"""

    file_location: Path = task_spec_location(task_spec_name)

    if file_location is None:
        warn_missing_file(task_spec_name)
        return

    task_spec: TaskSpec = deserialize_task_spec_file(file_location)

    file_meta = task_spec_file_metadata(file_location)
    obj_meta = task_spec_object_metadata(task_spec)

    title = typer.style(obj_meta["title"], bold=True)

    colored_keys = (
        typer.style(field, fg=typer.colors.BRIGHT_BLUE)
        for field in justified_with_colons(
            glot["title_descriptor"],
            glot["description_descriptor"],
            glot["full_path_descriptor"],
            glot["step_count_descriptor"],
            glot["context_vars_descriptor"],
            glot["last_accessed_descriptor"],
            glot["last_modified_descriptor"],
        )
    )

    meta_values = (
        title,
        obj_meta["description"],
        file_meta["full_path"],
        obj_meta["step_count"],
        obj_meta["context_vars"],
        file_meta["last_accessed"],
        file_meta["last_modified"],
    )

    for field, value in zip(colored_keys, meta_values):
        typer.echo(f"{field} {value}")
