"""pretty printing utilities for not"""
from functools import partial
from itertools import chain
from pathlib import Path
from textwrap import indent
from typing import Dict, Iterator


import typer

from .constants import (
    DirectoryChoicesForListCommand,
    DOT_NOTHING_DIRECTORY_NAME,
)
from .filesystem import (
    glob_each_extension,
    task_spec_names_by_parent_dir_name,
)
from .models import TaskSpecInspection


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


def spacious_print(*args):
    """Print with double newlines"""

    return partial(print, end="\n\n")


# TODO: on a given step, color the last line as code


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
