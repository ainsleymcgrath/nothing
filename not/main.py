import typer

from . import runner
from .parser_ import parse, NothingfileSpec


app = typer.Typer(help="Nothing helps coder be more smarter & less dumber.")


@app.command()
def do(instructions_document: str):
    """Go through the steps of a Nothing you have already created"""

    nothing: NothingfileSpec = parse(instructions_document)

    runner.run(nothing)


@app.command()
def new(name: str, destination_dir: str = None, notfile: str = None):
    """Template out a new nothing file to the nearest .nothing directory
    and open with $EDITOR"""
    pass


@app.command()
def edit(name: str, rename: bool = False):
    """Edit existing Nothing file"""
    pass


@app.command()
def copy(old_nothing: str, new_nothing: str):
    """Copy an old nothing file to a new one with the provided name"""
    pass


@app.command()
def describe(old_nothing: str, new_nothing: str):
    """Display a little summary of the Nothingfile"""
    pass
