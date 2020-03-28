from functools import partial
import typer


def dramatic_title(title):
    border = "=" * len(title)
    typer.echo(border)
    typer.echo(title)
    typer.echo(border)
    typer.echo()


spacious_print = partial(print, end="\n\n")
