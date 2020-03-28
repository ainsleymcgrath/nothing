import sys

from . import parser_
from . import runner
from .theatrics import dramatic_title, spacious_print

import typer


app = typer.Typer()


@app.command()
def do(instructions_document: str):
    """Go through the steps of a Nothing you have already created"""

    nothing: parser_.Nothing = parser_.parse(instructions_document)

    runner.run(nothing)


@app.command()
def new(name: str, destination_dir: str = None):
    """Template out a new nothing file to the nearest .nothing directory
    and open with $EDITOR"""
    pass


@app.command()
def edit(name: str):
    pass


@app.command()
def copy(old_nothing: str, new_nothing: str):
    pass
