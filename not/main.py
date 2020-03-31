import typer

from . import runner
from .parser_ import parse, TaskSpec


app = typer.Typer(help="Nothing helps coder be more smarter & less dumber.")


@app.command()
def do(task_spec_name: str):
    """Go through the steps of a Task Spec you have already created"""

    spec: TaskSpec = parse(task_spec_name)

    runner.run(spec)


@app.command()
def new(task_spec_name: str, destination_dir: str = None, as_notfile: bool = False):
    """Template out a new Task Spec to the nearest .nothing directory
    and open with $EDITOR"""
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
def describe(task_spec_name: str):
    """Display a little summary of the Task Spec"""
    pass
