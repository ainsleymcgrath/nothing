# pylint: disable=too-many-arguments

"""The subcommands of `not`"""
from pathlib import Path

import typer

from . import writer
from .constants import DirectoryChoicesForListCommand
from .models import TaskSpec, TaskSpecCreate, TaskSpecCreateExpert
from .reader import deserialize_task_spec_file
from .theatrics import (
    confirm_overwrite,
    interactive_walkthrough,
    multiprompt,
    show_fancy_list,
    show_task_spec_overview,
    success,
)

from .filesystem import task_spec_location


app = typer.Typer(help="Nothing helps coder be more smarter & less dumber.")


@app.command()
def do(task_spec_name: str):
    """Go through the steps of a Task Spec you have already created"""

    file_location: Path = task_spec_location(task_spec_name)

    with file_location.open() as file:
        task_spec: TaskSpec = deserialize_task_spec_file(file.read())

    if task_spec is None:
        typer.echo("Hmmm...doesn't look like there's a spec for that task.")
        return

    interactive_walkthrough(task_spec)


@app.command()
def new(
    ctx: typer.Context,
    task_spec_name: str = typer.Argument(None),
    destination_dir: Path = Path.cwd(),
    extension: str = "not",
    expert: bool = False,
    edit_after_write: bool = True,
    overwrite: bool = False,
    interactive: bool = True,  # make this a config default
):
    """Template out a new Task Spec to the nearest .nothing directory and open with
    $EDITOR. When no arguments are provided, Task Spec is configured interactively."""

    if interactive or task_spec_name is None:
        (
            task_spec_name,
            extension,
            destination_dir,
            expert,
            edit_after_write,
        ) = multiprompt(
            ("The title of your Task Spec", {}),
            ("Extension", {"default": extension}),
            ("Destination directory", {"default": destination_dir, "type": Path}),
            ("Extra config? (like --expert)", {"default": expert, "type": bool}),
            ("Open $EDITOR now?", {"default": edit_after_write, "type": bool}),
        )

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
            writer.write(task_spec_name, destination_dir.expanduser(), force=True)

    if edit_after_write:
        ctx.invoke(edit, task_spec_name=task_spec_name)

    success(f"{task_spec_filename} written to {destination_dir.resolve()}")


@app.command()
def edit(
    task_spec_name: str, rename: bool = False,
):
    """Edit existing Task Spec"""
    path_to_task_spec: Path = task_spec_location(task_spec_name).resolve()

    if rename:
        rename_prompt = typer.style(
            "What is the new name for the file? 📝", fg=typer.colors.BLUE
        )
        new_name = typer.prompt(rename_prompt)

    typer.edit(filename=str(path_to_task_spec))


@app.command()
def copy(existing_task_spec_name: str, new_task_spec_name: str):
    """Copy an old Task Spec to a new one with the provided name"""
    pass


@app.command()
def ls(include: DirectoryChoicesForListCommand = DirectoryChoicesForListCommand.both):
    """Display the location of every Task Spec in cwd and/or $HOME"""

    show_fancy_list(include)


@app.command()
def drop(existing_task_spec_name: str, no_confirm: bool = False):
    """Permanently delete a task spec file. Confirm before doing unless specified"""
    pass


@app.command()
def describe(task_spec_name: str):
    """Display a little summary of the Task Spec"""
    pass
