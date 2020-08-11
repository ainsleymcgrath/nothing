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


@app.command(help=glot["new_help"])
def new(
    ctx: typer.Context,
    procedure_name: str = typer.Option(
        None, "--name", "-N", is_eager=True, help=glot["new_procedure_name_option_help"]
    ),
    global_: bool = global_flag,
    skeleton: bool = typer.Option(
        False, "--skeleton", "-K", help=glot["new_skeleton_option_help"]
    ),
    no_edit_after: bool = no_edit_after_flag,
    overwrite: bool = typer.Option(
        False, "--overwrite", "-O", help=glot["new_overwrite_option_help"]
    ),
):
    """Subcommand for creating new Procedures"""

    destination_dir = HOME_DOT_NOTHING_DIR if global_ else CWD_DOT_NOTHING_DIR

    # keep ur eye on the ball, there be mutants here
    defaults = {
        "name": procedure_name,
        "default_destination": friendly_prefix_for_path(destination_dir),
        "no_edit_after": no_edit_after,
    }

    if not skeleton:
        (
            title,
            description,
            procedure_name,
            destination_dir,
            no_edit_after,
        ) = prompt_for_new_args(**defaults)

    # just in case the user gave a path with a ~ in it
    destination_dir = Path(destination_dir).expanduser()

    procedure_filename = f"{procedure_name}{PROCEDURE_EXT}"
    if skeleton:
        procedure = Procedure(
            path=destination_dir / procedure_filename,
            title=glot["skeleton_title"],
            description=glot["skeleton_description"],
            steps=glot["skeleton_steps"],
            context=[glot["skeleton_context_name_name"]],
            knowns=[{glot["skeleton_knowns_name"]: glot["skeleton_knowns_value"]}],
        )
    else:
        procedure = Procedure(
            path=destination_dir / procedure_filename,
            title=title,
            description=description,
            steps=glot["steps_placeholder"],
        )

    try:
        writer.write(procedure, force=overwrite)
    except FileExistsError:
        if confirm_overwrite(procedure_name):
            writer.write(procedure, force=True)

    # pylint: disable=import-outside-toplevel
    if not no_edit_after:
        # this is a special occasion!
        from importlib import reload
        from . import filesystem

        # `state` in filesystem needs to be recalculated on account of the new
        # file in the directories it looks at.
        # importlib does the trick!
        reload(filesystem)

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
def info(procedure_name: str = completable_procedure_name_argument):
    """Display a little overview of the Procedure"""

    show_dossier(procedure_name)
