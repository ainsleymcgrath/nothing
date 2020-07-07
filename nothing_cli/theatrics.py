"""pretty printing utilities for not"""
from itertools import chain
from pathlib import Path
from textwrap import indent
from string import Formatter
from typing import Any, Dict, Iterator, List, Set, Tuple

from slugify import slugify
import typer

from .constants import DirectoryChoicesForListCommand, LAZY_CONTEXT_PREFIX

from .localization import polyglot as glot
from .filesystem import (
    collect_fancy_list_input,
    deserialize_procedure_file,
    procedure_file_metadata,
    procedure_location,
    procedure_object_metadata,
)
from .models import ContextItem, Step, Procedure


WARNING_STYLE = {"fg": typer.colors.YELLOW}


def marquis(title, description):
    """A display of the title + description that

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     Looks Like This

        'With a description in quotes'
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    border_length = max(len(title), len(description)) + 8
    border = "~" * border_length
    styled_title = typer.style(f" {title} ", bold=True, fg=typer.colors.MAGENTA)

    typer.echo(border)
    typer.echo()
    typer.echo(styled_title)
    typer.echo(f"    '{description}' ")
    typer.echo()
    typer.echo(border)
    typer.echo()


# pylint: disable=no-self-use
class InterpolationStore:
    """Eventually provides access to the value of each variable provided
    in the `context` and `knowns` fields of a Procedure.
    In other words, it stores all the values needed to call .format() with
    to display a step in the source procedure.

    Any keyname beginning with a __ is 'lazy'. The user is prompted for that before
    the first time it is referenced, then it's stored.
    The user is prompted for values of keys with regular during __init__.
    Values from `knowns` are stored immediately."""

    def __init__(self, procedure: Procedure):

        self.procedure = procedure
        self.store: Dict[str, str] = {}
        self.requisite_names = set(
            chain(
                (next(iter(p.keys())) for p in procedure.knowns),
                (c.var_name for c in procedure.context),
            )
        )

        for known in procedure.knowns:
            k, v = next(iter(known.items()))
            self.store[k] = v

        eager_context_items = [
            item
            for item in procedure.context
            if not item.var_name.startswith(LAZY_CONTEXT_PREFIX)
        ]

        for item in eager_context_items:
            self.store[item.var_name] = self.prompt_for_value(item)

    def prompt_for_value(self, item: ContextItem) -> str:
        """Use ContextItem.prompt to get a value from the user.
        Here for easier test patching, mostly."""

        value = ask(item.prompt)

        return value

    def get_interpolations(self, step: Step) -> Dict:
        """Returns the dictionary of kwargs the step needs for .format()"""

        key_names = self.get_format_names(step.prompt)
        if not key_names.issubset(self.requisite_names):
            warning = typer.style(
                glot.localized("undefined_variable_warn", {"step_number": step.number}),
                **WARNING_STYLE,
            )
            typer.echo(warning)
            raise typer.Abort()

        for key in key_names:
            if key not in self.store:
                context: ContextItem = next(
                    c for c in self.procedure.context if c.var_name == key
                )
                self.store[key] = self.prompt_for_value(context)

        return {k: v for k, v in self.store.items() if k in key_names}

    def get_format_names(self, text: str) -> Set[str]:
        """Return the names of any variables mentioned in the templates of `text`"""

        formatter = Formatter()

        return set(
            template_name
            for _, template_name, _, _ in formatter.parse(text)
            if template_name is not None
        )


def interactive_walkthrough(procedure: Procedure) -> None:
    """Interactively walk through a Procedure"""

    marquis(procedure.title, procedure.description)

    store = InterpolationStore(procedure)

    typer.echo()
    for step in procedure.steps:
        step_header = typer.style(
            # XXX why do steps know their numbers? :thinking:
            f"{glot['step_prefix']} {step.number}:",
            bg=typer.colors.WHITE,
            fg=typer.colors.BLACK,
        )
        typer.echo(step_header)

        interpolations = store.get_interpolations(step)
        step_body = styled_step(step.prompt.format(**interpolations))

        typer.echo(step_body)

        input(glot["nag"])
        typer.echo()

    finale = typer.style(glot["completion_message"], fg=typer.colors.GREEN, bold=True)
    typer.echo(finale)


def styled_step(step_body: str) -> str:
    """Bold the incoming text and color the last line if there are more than 1 lines"""

    lines = step_body.split("\n")
    regular_line_style = {"bold": True, "fg": typer.colors.BLUE}
    last_line_style = {"bold": True, "fg": typer.colors.MAGENTA}

    if len(lines) > 1:
        last_line = typer.style(lines.pop(), **last_line_style)
        styled_lines = [typer.style(line, **regular_line_style) for line in lines]

        return "\n".join([*styled_lines, last_line]) + "\n"

    return typer.style(step_body, **regular_line_style) + "\n"


def multiprompt(*prompts: Tuple[str, Dict]) -> Iterator[Any]:
    """Allows the caller to receive the values from a series of prompts
    in the order they were passed. A "prompt" here is a tuple containing an
    echo-able (usually a string), dictionary of any kwargs to pass to typer.prompt."""

    for prompt, prompt_kwargs in prompts:
        value = ask(prompt, **prompt_kwargs)

        yield value


def prompt_for_new_args(
    name=None, default_extension=None, default_destination=None, edit_after_write=None
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


def show_fancy_list(showing_from_dir: DirectoryChoicesForListCommand):
    """Show a pretty output of the Procedure files contained in the specified dir."""

    procedure_names_by_directory: Dict = collect_fancy_list_input(showing_from_dir)

    for base_dir, subdir_dict in procedure_names_by_directory.items():
        header = typer.style(
            f"[ {glot['GLOBAL'] if base_dir == 'home' else glot['LOCAL']} ]\n",
            typer.colors.BRIGHT_BLUE,
        )
        typer.echo(header)

        for dir_name, procedure_list in subdir_dict.items():
            subdir_header = typer.style(
                indent(f"{dir_name}/", "  "), fg=typer.colors.CYAN
            )
            typer.echo(subdir_header)

            for i, name in enumerate(procedure_list):
                typer.echo(indent(name, "    "))
                if i == len(procedure_list) - 1:
                    typer.echo()


def confirm_overwrite(procedure_name) -> bool:
    """Prompt y/n when user is attempting to create a Procedure with the same
    name as an existing one"""

    existence_warning = typer.style(
        glot.localized("overwrite_warn", {"name": procedure_name}), **WARNING_STYLE
    )

    return typer.confirm(existence_warning, abort=True)


def confirm_drop(procedure_name) -> bool:
    """Prompt y/n when user is about to delete a Procedure file"""

    drop_is_destructive_warning = typer.style(
        glot.localized("drop_warn", {"name": procedure_name}), **WARNING_STYLE
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


def config_exists_warn(warning):
    """Inform user that the file exists.
    Suggest they delete it if they want a new one"""

    message = typer.style(warning, **WARNING_STYLE)
    typer.echo("⚠️  " + message)
    typer.echo(glot["delete_suggestion"])


# TODO: raise typer.Abort() when called
def warn_missing_file(name):
    """A generic warning when a Procedure with the specified name does not exist"""

    message = typer.style(
        glot.localized("missing_file_warn", {"name": name}), **WARNING_STYLE
    )
    typer.echo(message)


def justified_with_colons(*strings) -> List[str]:
    """For use when making lists like so:

    Item       :   yep
    Another    :   sure

    Will use the longest word's len + 4 for the width."""
    width = len(max(strings, key=len)) + 4

    return [string.ljust(width, " ") + ": " for string in strings]


def show_dossier(procedure_name):
    """A pretty-printed overview of some Procedure metadata"""

    file_location: Path = procedure_location(procedure_name)

    if file_location is None:
        warn_missing_file(procedure_name)
        return

    procedure: Procedure = deserialize_procedure_file(file_location)

    file_meta = procedure_file_metadata(file_location)
    obj_meta = procedure_object_metadata(procedure)

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
