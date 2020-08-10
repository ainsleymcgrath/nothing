# pylint: disable=too-many-arguments

"""The subcommands of `not`"""
from pathlib import Path

import typer

from . import writer
from .constants import CWD_DOT_NOTHING_DIR, HOME_DOT_NOTHING_DIR, PROCEDURE_EXT
from .filesystem import (
    deserialize_procedure_file,
    friendly_prefix_for_path,
    path_to_write_to,
    procedure_location,
    reset_state,
)
from .localization import polyglot as glot
from .models import Procedure
from .subcommand_shared import (
    completable_procedure_name_argument,
    global_flag,
    no_edit_after_flag,
)
from .theatrics import (
    ask,
    config_exists_warn,
    confirm_drop,
    confirm_overwrite,
    interactive_walkthrough,
    prompt_for_new_args,
    show_dossier,
    show_fancy_list,
    success,
    warn_missing_file,
)

app = typer.Typer(help=glot["help"])


@app.command(help=glot["init_help"])
def init():
    """Command to create a .nothing directory locally"""

    if CWD_DOT_NOTHING_DIR.exists():
        config_exists_warn(glot["cwd_dot_nothing_exists_warn"])
    else:
        CWD_DOT_NOTHING_DIR.mkdir()
        success(glot["made_cwd_dot_nothing_dir"])


@app.command(help=glot["sample_help"])
def sample(global_: bool = False):
    """Write a cutesy sample Procedure."""

    destination = path_to_write_to(global_)
    writer.write_easter(destination)
    success(glot.localized("made_sample_procedure", {"directory": destination}))


@app.command()
def do(procedure_name: str = completable_procedure_name_argument):
    """Go through the steps of a Procedure you have already created"""

    file_location: Path = procedure_location(procedure_name)

    if file_location is None:
        warn_missing_file(procedure_name)
        raise typer.Abort

    procedure: Procedure = deserialize_procedure_file(file_location)

    interactive_walkthrough(procedure)


def _empty_callback(ctx: typer.Context, value: bool):
    """Ensure --empty/-E is always called with --name/-N specified"""

    empty_called_without_name = ctx.params.get("procedure_name") is None and value

    if empty_called_without_name:
        raise typer.BadParameter(glot["new_empty_callback_warning"])

    return value


@app.command(help=glot["new_help"])
def new(
    ctx: typer.Context,
    procedure_name: str = typer.Option(
        None, "--name", "-N", is_eager=True, help=glot["new_procedure_name_option_help"]
    ),
    global_: bool = global_flag,
    empty: bool = typer.Option(
        False,
        "--empty",
        "-E",
        callback=_empty_callback,
        help=glot["new_empty_option_help"],
    ),
    no_edit_after: bool = no_edit_after_flag,
    overwrite: bool = typer.Option(
        False, "--overwrite", "-O", help=glot["new_overwrite_option_help"]
    ),
):
    """Subcommand for creating new Procedures"""

    destination_dir = HOME_DOT_NOTHING_DIR if global_ else CWD_DOT_NOTHING_DIR

    # keep ur eye on the ball, there be mutants here
    if not empty:
        defaults = {
            "name": procedure_name,
            "default_destination": friendly_prefix_for_path(destination_dir),
            "no_edit_after": no_edit_after,
        }

        (
            title,
            description,
            procedure_name,
            destination_dir,
            edit_after,
        ) = prompt_for_new_args(**defaults)
        # just in case the user gave a path with a ~ in it
        destination_dir = Path(destination_dir).expanduser()

    procedure_filename = f"{procedure_name}.{PROCEDURE_EXT}"
    if empty:
        procedure = Procedure(
            filename=procedure_filename,
            description=glot["default_description"],
            steps=glot["default_steps"],
            context=[glot["default_context_name_name"]],
            knowns=[{glot["default_knowns_name"]: glot["default_knowns_value"]}],
        )
    else:
        procedure = Procedure(
            title=title, description=description, filename=procedure_filename
        )

    try:
        writer.write(procedure, destination_dir, force=overwrite)
    except FileExistsError:
        if confirm_overwrite(procedure_name):
            writer.write(procedure, destination_dir, force=True)

    if edit_after:
        reset_state()
        ctx.invoke(edit, procedure_name=procedure_name)

    success(
        glot.localized(
            "file_written",
            {"filename": procedure_filename, "destination": destination_dir.resolve()},
        )
    )


@app.command()
def edit(
    procedure_name: str = completable_procedure_name_argument, rename: bool = False
):
    """Edit existing Procedure with $EDITOR"""

    path_to_procedure: Path = procedure_location(procedure_name)

    if path_to_procedure is None:
        warn_missing_file(procedure_name)
        raise typer.Abort()

    if rename:
        new_name = ask(glot["filename_prompt"])
        path_to_procedure.rename(path_to_procedure.parent / new_name)
        success(
            glot.localized(
                "file_renamed", {"name": new_name, "old_name": procedure_name}
            )
        )

    typer.edit(filename=str(path_to_procedure))
    success(glot.localized("file_edited", {"name": procedure_name}))


@app.command()
def ls():
    """Display the location of every Procedure in cwd and/or $HOME"""

    show_fancy_list()


@app.command()
def drop(
    procedure_name: str = completable_procedure_name_argument, no_confirm: bool = False
):
    """Permanently delete a Procedure file. Confirm before doing unless specified"""

    file: Path = procedure_location(procedure_name)

    if file is None:
        warn_missing_file(procedure_name)
        raise typer.Abort()

    if no_confirm or confirm_drop(procedure_name):
        file.unlink()
        success(
            glot.localized("dropped", {"name": procedure_name, "location": file.parent})
        )


@app.command()
def describe(procedure_name: str = completable_procedure_name_argument):
    """Display a little overview of the Procedure"""

    show_dossier(procedure_name)
