# pylint: disable=too-many-arguments

"""The subcommands of `not`"""
from pathlib import Path

import typer

from . import writer
from .config import GlobalConfig
from .constants import DirectoryChoicesForListCommand
from .filesystem import deserialize_task_spec_file
from .localization import polyglot as glot
from .models import TaskSpec, TaskSpecCreate, TaskSpecCreateExpert
from .theatrics import (
    ask,
    confirm_overwrite,
    interactive_walkthrough,
    warn_missing_file,
    prompt_for_copy_args,
    prompt_for_new_args,
    show_fancy_list,
    # show_task_spec_overview,
    success,
)

from .filesystem import task_spec_location


app = typer.Typer(help=glot["help"])
config = GlobalConfig()


@app.command()
def do(task_spec_name: str):
    """Go through the steps of a Task Spec you have already created"""

    file_location: Path = task_spec_location(task_spec_name)

    if file_location is None:
        warn_missing_file(task_spec_name)
        return

    with file_location.open() as file:
        task_spec: TaskSpec = deserialize_task_spec_file(file.read())

    interactive_walkthrough(task_spec)


@app.command()
def new(
    ctx: typer.Context,
    task_spec_name: str = typer.Argument(None),
    destination_dir: Path = config.default_destination_dir,
    extension: str = "not",
    expert: bool = False,
    edit_after_write: bool = config.edit_after_write,
    overwrite: bool = False,
    interactive: bool = config.interactive_new,
):
    """Template out a new Task Spec to the nearest .nothing directory and open with
    $EDITOR. When no arguments are provided, Task Spec is configured interactively."""

    if interactive or task_spec_name is None:
        defaults = {
            "default_extension": extension,
            "default_destination": destination_dir,
            "expert": expert,
            "edit_after_write": edit_after_write,
        }

        (
            task_spec_name,
            extension,
            destination_dir,
            expert,
            edit_after_write,
        ) = prompt_for_new_args(**defaults)
        # XXX how to skip prompt when name is specified?

    task_spec_filename = f"{task_spec_name}.{extension}"
    task_spec: TaskSpec = (
        TaskSpecCreate(filename=task_spec_filename)
        if not expert
        else TaskSpecCreateExpert(filename=task_spec_filename)
    )

    try:
        writer.write(
            task_spec, destination_dir.expanduser(), force=interactive or overwrite
        )
    except FileExistsError:
        if confirm_overwrite(task_spec_name):
            writer.write(task_spec, destination_dir.expanduser(), force=True)

    if edit_after_write:
        ctx.invoke(edit, task_spec_name=task_spec_name)

    success(
        glot.localized(
            "file_written",
            {"filename": task_spec_filename, "destination": destination_dir.resolve()},
        )
    )


@app.command()
def edit(task_spec_name: str, rename: bool = False):
    """Edit existing Task Spec"""
    path_to_task_spec: Path = task_spec_location(task_spec_name).resolve()

    if rename:
        new_name = ask(glot["filename_prompt"])
        path_to_task_spec.rename(path_to_task_spec.parent / new_name)

    typer.edit(filename=str(path_to_task_spec))
    success(glot.localized("file_edited", {"name": "task_spec_name"}))


@app.command()
def copy(
    ctx: typer.Context,
    existing_task_spec_name: str,
    new_task_spec_name=typer.Argument(None),
    new_title: str = None,
    destination_dir: Path = None,
    new_extension: str = None,
    edit_after_write: bool = False,
):
    """Copy an old Task Spec to a new one with the provided name"""

    original_file: Path = task_spec_location(existing_task_spec_name)

    if original_file is None:
        warn_missing_file(existing_task_spec_name)
        return

    old_task_spec: TaskSpec = deserialize_task_spec_file(original_file)
    interactive = existing_task_spec_name is not None or new_task_spec_name is not None

    if interactive:
        extension_without_dot = original_file.suffix.lstrip(".")
        defaults = {
            "default_title": old_task_spec.title,
            "default_destination": original_file.parent,  # TODO use friendly prefix
            "default_extension": extension_without_dot,  # TODO enum for extensions
            "edit_after_write": edit_after_write,
        }

        (
            new_task_spec_name,
            new_title,
            destination_dir,
            new_extension,
            edit_after_write,
        ) = prompt_for_copy_args(**defaults)

    new_filename = f"{new_task_spec_name}.{new_extension}"
    new_task_spec: TaskSpec = old_task_spec.copy(
        update={"filename": new_filename, "title": new_title}
    )

    try:
        writer.write(new_task_spec, destination_dir.expanduser())
    except FileExistsError:
        if confirm_overwrite(new_task_spec_name):
            writer.write(new_task_spec, destination_dir.expanduser(), force=True)

    if edit_after_write:
        ctx.invoke(edit, task_spec_name=new_task_spec_name)

    success(
        glot.localized(
            "copied",
            {"name": existing_task_spec_name, "destination": destination_dir.resolve()},
        )
    )


@app.command()
def ls(include: DirectoryChoicesForListCommand = DirectoryChoicesForListCommand.both):
    """Display the location of every Task Spec in cwd and/or $HOME"""

    show_fancy_list(include)


@app.command()
def drop(existing_task_spec_name: str, no_confirm: bool = False):
    """Permanently delete a task spec file. Confirm before doing unless specified"""


@app.command()
def describe(task_spec_name: str):
    """Display a little overview of the Task Spec"""
    # count steps
    # created / modified date
    # title, description, author
