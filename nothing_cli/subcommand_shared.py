"""Bits of functionality shared across the subcommands in main"""
from pathlib import Path
from typing import List, Tuple

import typer

from .filesystem import deserialize_procedure_file, state
from .localization import polyglot as glot
from .models import Procedure

procedures: List[Tuple[Path, Procedure]] = [
    (path, deserialize_procedure_file(path)) for path in state()
]


def procedure_name_completions(incomplete: str):
    """Triggered on [TAB] [TAB] for commands that use it.
    Displays the list of procedures in CWD and home
    along with their descriptions for clarity"""

    for path, proc in procedures:
        if incomplete in proc.name:
            yield path.stem, f"'{proc.description}'"


completable_procedure_name_argument: typer.Argument = typer.Argument(
    str, autocompletion=procedure_name_completions
)

no_edit_after_flag = typer.Option(
    True,
    "--no-edit-after",
    "-A",
    help=glot["edit_after_option_help"],
    show_default=True,
)

global_flag = typer.Option(False, "--global", "-G", help=glot["new_global_option_help"])
