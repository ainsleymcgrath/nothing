"""The subcommands of `not`"""
from pathlib import Path

import typer

from . import runner
from . import writer
from .models import TaskSpec, TaskSpecCreate, TaskSpecCreateExpert
from .reader import serialize_task_spec_file

# from .theatrics import show_task_spec_overview
from .utils import task_spec_location

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
    task_spec_name: str,
    destination_dir: Path = Path.cwd(),
    extension: str = "not",
    expert: bool = True,
    edit_after_write: bool = True,
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
        writer.write(task_spec, destination_dir)
    except FileExistsError:
        existence_warning = typer.style(
            f"🤔 Task Spec '{task_spec_name}' appears to exist already",
            fg=typer.colors.YELLOW,
        )
        typer.echo(existence_warning)
        # show_task_spec_overview(inspect(task_spec))

        # TODO: Prompt some options: edit, overwrite, inspect, rename existing spec
        return

    success_message = typer.style("Success! 🙌", fg=typer.colors.GREEN)
    typer.echo(success_message)
    typer.echo(f"{task_spec_filename} written to {destination_dir.resolve()}")

    if edit_after_write:
        # TODO: open with the editor
        pass


@app.command()
def edit(task_spec_name: str, rename: bool = False):
    """Edit existing Task Spec"""
    pass


@app.command()
def copy(existing_task_spec_name: str, new_task_spec_name: str):
    """Copy an old Task Spec to a new one with the provided name"""
    pass


@app.command()
def list(show_home: bool = True, show_local: bool = True, show_global: bool = False):
    """Pretty print the location of every Task Spec file in cwd and ~.
    If --global, find every Task Spec on the machine."""


@app.command()
def drop(existing_task_spec_name: str, no_confirm: bool = False):
    """Permanently delete a task spec file. Confirm before doing unless specified"""
    pass


@app.command()
def describe(task_spec_name: str):
    """Display a little summary of the Task Spec"""
    pass
