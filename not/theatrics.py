from functools import partial
import typer

from .models import TaskSpecInspection


def dramatic_title(title):
    border = "=" * len(title)
    typer.echo(border)
    typer.echo(title)
    typer.echo(border)
    typer.echo()


spacious_print = partial(print, end="\n\n")

# TODO: on a given step, color the last line as code


def show_task_spec_overview(inspection: TaskSpecInspection):
    pass
