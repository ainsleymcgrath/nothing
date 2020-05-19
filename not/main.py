# pylint: disable=too-many-arguments

"""The subcommands of `not`"""
from pathlib import Path

import typer

from . import runner
from . import writer
from .constants import DirectoryChoicesForListCommand
from .models import TaskSpec, TaskSpecCreate, TaskSpecCreateExpert
from .reader import serialize_task_spec_file
from .theatrics import show_fancy_list

# from .theatrics import show_task_spec_overview
from .filesystem import task_spec_location

# from .utils import inspect


app = typer.Typer(help="Nothing helps coder be more smarter & less dumber.")


@app.command()
def do(task_spec_name: str):
    """Go through the steps of a Task Spec you have already created"""

    file_location: Path = task_spec_location(task_spec_name)

    with file_location.open() as file:
        task_spec: TaskSpec = serialize_task_spec_file(file.read())

    if task_spec is None:
        typer.echo("Hmmm...doesn't look like there's a spec for that task.")
        return

    runner.run(task_spec)


@app.command()
def new(
    ctx: typer.Context,
    task_spec_name: str,
    destination_dir: Path = Path.cwd(),
    extension: str = "not",
    expert: bool = False,
    edit_after_write: bool = True,
    overwrite: bool = False,
):
    """Template out a new Task Spec to the nearest .nothing directory
    and open with $EDITOR"""

    task_spec_filename = f"{task_spec_name}.{extension}"
    task_spec: TaskSpec = (
        TaskSpecCreate(filename=task_spec_filename)
        if not expert
        else TaskSpecCreateExpert(filename=task_spec_filename)
    )

    try:
        writer.write(task_spec, destination_dir, force=overwrite)
    except FileExistsError:
        # TODO lift this block into theatrics
        existence_warning = typer.style(
            f"🤔 Task Spec '{task_spec_name}' appears to exist already\n"
            "Would you like to overwrite it?",
            fg=typer.colors.YELLOW,
        )

        if typer.confirm(existence_warning, abort=True):
            writer.write(task_spec, destination_dir, force=True)

        # TODO: Prompt some options: edit, overwrite, inspect, rename existing spec

    if edit_after_write:
        ctx.invoke(edit, task_spec_name=task_spec_name)

    success_message = typer.style("Success! 🙌", fg=typer.colors.GREEN)
    typer.echo(success_message)
    typer.echo(f"{task_spec_filename} written to {destination_dir.resolve()}")


@app.command()
def edit(
    task_spec_name: str,
    rename: str = typer.Option(
        prompt="What should the new name be?", default="", confirmation_prompt=True
    ),
):
    """Edit existing Task Spec"""

    path_to_task_spec: Path = task_spec_location(task_spec_name).resolve()
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
