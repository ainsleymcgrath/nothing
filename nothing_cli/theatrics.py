"""pretty printing utilities for not"""
from pathlib import Path
from string import Formatter
from textwrap import indent
from typing import Any, Dict, Iterator, List, Set, Tuple, Union

import typer
from click import Choice
from slugify import slugify

from .constants import LAZY_CONTEXT_PREFIX, MISSING_INFO_PALCEHOLDER
from .filesystem import (
    collect_fancy_list_input,
    deserialize_procedure_file,
    procedure_file_metadata,
    procedure_location,
    procedure_object_metadata,
)
from .localization import polyglot as glot
from .models import Procedure, context_var_name

WARNING_STYLE = {"fg": typer.colors.YELLOW}


def marquis(title, description):
    """A display of the title + description that

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     Looks Like This

        'With a description in quotes'
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    border_length = max(len(title), len(description or "")) + 8
    border = "~" * border_length
    styled_title = typer.style(f" {title} ", bold=True, fg=typer.colors.MAGENTA)

    typer.echo(border)
    typer.echo()
    typer.echo(styled_title)
    if description:
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

        self.procedure: Procedure = procedure
        self.store: Dict[str, str] = {}
        self.requisite_names: Set = {
            *(next(iter(p.keys())) for p in procedure.knowns),
            *(context_var_name(c) for c in procedure.context),
        }

        if not self.requisite_names:
            return

        if procedure.knowns:
            for known in procedure.knowns:
                k, v = next(iter(known.items()))
                self.store[k] = v

        eager_context_items = (
            item
            for item in procedure.context
            if not context_var_name(item).startswith(LAZY_CONTEXT_PREFIX)
        )

        for item in eager_context_items:
            self.store[context_var_name(item)] = self.prompt_for_value(item)

    def prompt_for_value(self, item: Union[str, Dict]) -> str:
        """Either use the provided prompt to ask for a variables value, or ask
        with the default prompt if one was not provided."""

        value = ask(
            glot["default_context_prompt"].format(item)
            if isinstance(item, str)
            else next(iter(item.values()))
        )

        return value

    def get_interpolations(self, step: str, index: int) -> Dict:
        """Returns the dictionary of kwargs the step needs for .format()"""

        key_names = self.get_format_names(step)

        if not key_names.issubset(self.requisite_names):
            warning = typer.style(
                glot.localized("undefined_variable_warn", {"step_number": index + 1}),
                **WARNING_STYLE,
            )
            typer.echo(warning)
            raise typer.Abort()

        for key in key_names:
            if key not in self.store:
                context: Union[str, Dict] = next(
                    c for c in self.procedure.context if context_var_name(c) == key
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
    for i, step in enumerate(procedure.steps):
        step_header = typer.style(
            f"{glot['step_prefix']} {i}:", bg=typer.colors.WHITE, fg=typer.colors.BLACK
        )
        typer.echo(step_header)

        interpolations = store.get_interpolations(step, i)
        step_body = styled_step(step.format(**interpolations))

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
    name=None, default_destination="cwd", edit_after=None
) -> Iterator[Any]:
    """Prompt for all arguments needed to perform `not do`"""

    title = ask(glot["new_title_prompt"])
    name = slugify(title) if name is None else name

    prompts = (
        (glot["new_description_prompt"], {"default": ""}),
        (glot["new_name_prompt"], {"default": name}),
        (
            glot["new_destination_prompt"],
            {
                "default": default_destination,
                "type": Choice(["home", "cwd"]),
                "show_choices": True,
            },
        ),
        (glot["new_open_editor_prompt"], {"default": edit_after, "type": bool}),
    )

    return (title, *multiprompt(*prompts))


def show_fancy_list():
    """Show a pretty output of the Procedure files contained in the specified dir."""

    procedure_names_by_directory: Dict = collect_fancy_list_input()

    typer.echo()
    for base_dir, procedure_names in procedure_names_by_directory.items():
        header = typer.style(
            f"[ {glot['GLOBAL'] if base_dir == 'global' else glot['LOCAL']} ]\n",
            typer.colors.BRIGHT_BLUE,
        )
        typer.echo(header)

        names_count = len(procedure_names)

        for i, name in enumerate(procedure_names):
            typer.echo(indent(name, " " * 4))

            if i == names_count - 1:
                # newline after the last item
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
            glot["knowns_descriptor"],
            glot["last_accessed_descriptor"],
            glot["last_modified_descriptor"],
        )
    )

    meta_values = (
        title,
        obj_meta["description"] or MISSING_INFO_PALCEHOLDER,
        file_meta["full_path"],
        obj_meta["step_count"],
        obj_meta["context_vars"] or MISSING_INFO_PALCEHOLDER,
        # knowns will look like [ name=value, other_name=other_value ] etc
        ["=".join(k.popitem()) for k in obj_meta["knowns"]] or MISSING_INFO_PALCEHOLDER,
        file_meta["last_accessed"],
        file_meta["last_modified"],
    )

    for field, _value in zip(colored_keys, meta_values):
        # strip the quotes off any list items for human-ness
        value = f'[ {", ".join(_value)} ]' if isinstance(_value, list) else _value
        typer.echo(f"{field} {value}")
