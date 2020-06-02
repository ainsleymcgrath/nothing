"""pretty printing utilities for not"""
from itertools import chain
from pathlib import Path
from textwrap import indent
from typing import Any, Dict, Iterator, Tuple


import typer

from .config import GlobalConfig
from .constants import (
    DirectoryChoicesForListCommand,
    DOT_NOTHING_DIRECTORY_NAME,
)
from .filesystem import (
    glob_each_extension,
    task_spec_names_by_parent_dir_name,
)
from .models import Step, TaskSpec, TaskSpecInspection


config = GlobalConfig()


def dramatic_title(title):
    """A title that

    ###############
    Looks Like This
    ###############
    """

    border = "=" * len(title)
    typer.echo(border)
    typer.echo(title)
    typer.echo(border)
    typer.echo()


def interactive_walkthrough(task_spec: TaskSpec) -> None:
    """Interactively walk through a task spec"""

    # XXX use spec-level config
    dramatic_title(f"{config.title_prefix}: {task_spec.title}")

    context_dict = {}

    if task_spec.context:
        for item in task_spec.context:
            context_value = typer.prompt(item.prompt)
            context_dict[item.var_name] = context_value

    typer.echo()
    for step in task_spec.steps:
        run_step(
            step, context_dict,
        )

    typer.echo(config.completion_message)


def run_step(step: Step, context: Dict):
    """Run just one Step in a TaskSpec"""
    typer.echo(f"{config.step_prefix} {step.number}:")

    try:
        typer.echo(step.prompt.format(**context) + "\n")
    except KeyError:
        typer.echo(step.prompt + "\n")

    input("Press enter to continue...")
    typer.echo()


def multiprompt(*prompts: Tuple[str, Dict]) -> Iterator[Any]:
    """Allows the caller to receive the values from a series of prompts
    in the order they were passed. A "prompt" here is a tuple containing an
    echo-able (usually a string), dictionary of any kwargs to pass to typer.prompt."""

    for prompt, prompt_kwargs in prompts:
        value = ask(prompt, **prompt_kwargs)

        yield value


def prompt_for_new_args(
    default_extension=None, default_destination=None, expert=None, edit_after_write=None
) -> Iterator[Any]:
    """Prompt for all arguments needed to perform `not do`"""

    prompts = (
        ("The title of your Task Spec", {}),
        ("Extension", {"default": default_extension}),
        ("Destination directory", {"default": default_destination, "type": Path}),
        ("Extra config? (like --expert)", {"default": expert, "type": bool}),
        ("Open $EDITOR now?", {"default": edit_after_write, "type": bool}),
    )

    return multiprompt(*prompts)


def prompt_for_copy_args(
    default_title=None,
    default_destination=None,
    default_extension=None,
    edit_after_write=None,
) -> Iterator[Any]:
    """Prompt for all arguments needed to perform `not copy`"""

    prompts = (
        ("New Task Spec name", {}),
        ("New Task Spec title", {"default": default_title, "type": str}),
        ("Destination dir for copy", {"default": default_destination, "type": Path}),
        ("Extension for new Task Spec", {"default": default_extension, "type": str}),
        ("Edit after write?", {"default": edit_after_write, "type": bool},),
    )

    return multiprompt(*prompts)


def show_task_spec_overview(inspection: TaskSpecInspection):
    pass


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
            "*", (Path.home() / DOT_NOTHING_DIRECTORY_NAME), recurse=True
        )

        names_by_dir["home"] = task_spec_names_by_parent_dir_name(
            task_specs_in_home_dot_nothing_dir, base_dir="home"
        )

    if show_cwd or show_both:
        task_specs_in_cwd_dot_nothing_dir: Iterator[Path] = glob_each_extension(
            "*", Path.cwd(), recurse=True
        )
        dot_not_files_in_cwd = Path.cwd().glob("**/*.not")
        any_task_specs_in_cwd = chain(
            task_specs_in_cwd_dot_nothing_dir, dot_not_files_in_cwd
        )

        names_by_dir["cwd"] = task_spec_names_by_parent_dir_name(
            any_task_specs_in_cwd, base_dir="cwd"
        )

    return names_by_dir


def show_fancy_list(showing_from_dir: DirectoryChoicesForListCommand):
    """Show a pretty output of the task spec files contained in the specified dir."""

    task_spec_names_by_directory: Dict = _collect_fancy_list_input(showing_from_dir)

    for base_dir, subdir_dict in task_spec_names_by_directory.items():
        header = typer.style(
            f"[ {'GLOBAL' if base_dir == 'home' else 'LOCAL'} ]\n",
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
        f"🤔 Task Spec '{task_spec_name}' appears to exist already\n"
        "Would you like to overwrite it?",
        fg=typer.colors.YELLOW,
    )

    return typer.confirm(existence_warning, abort=True)


def success(message) -> None:
    """Echo the message with a stylish interjection above it"""

    stylish_interjection = typer.style("Success! 🙌", fg=typer.colors.GREEN)
    typer.echo(stylish_interjection)
    typer.echo(message)


def ask(question, **prompt_kwargs) -> Any:
    """Prompt the user with a question"""

    styled_question = typer.style(question, fg=typer.colors.BRIGHT_BLACK)
    answer = typer.prompt(styled_question, **prompt_kwargs)

    return answer


def warn_missing_file(name):
    """A generic warning when a Task Spec with the specified name does not exist"""

    message = typer.style(
        f"😕 It doesn't look like there's a spec for '{name}'.", fg=typer.colors.YELLOW
    )
    typer.echo(message)
