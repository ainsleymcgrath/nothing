# pylint: disable=too-many-arguments

"""The subcommands of `not`"""

from pathlib import Path

import typer

from . import writer
from .constants import CWD_DOT_NOTHING_DIR, HOME_DOT_NOTHING_DIR, PROCEDURE_EXT, VERSION
from .filesystem import (
    deserialize_procedure_file,
    friendly_prefix_for_path,
    procedure_location,
)
from .localization import polyglot as glot
from .models import Procedure
from .subcommand_shared import (
    completable_procedure_name_argument,
    edit_after_flag,
    global_flag,
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


def _version_callback(value: bool):
    if value:
        typer.echo(VERSION)
        raise typer.Exit()


# pylint: disable=unused-argument
@app.callback()
def _(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help=glot["version_help"],
    )
):
    """This unnamed function is for registering any --options that ought to be attached
    to the `not` command itself, and not any subcommands."""


@app.command(help=glot["init_help"])
def init():
    """Command to create a .nothing directory locally"""

    if CWD_DOT_NOTHING_DIR.exists():
        config_exists_warn(glot["cwd_dot_nothing_exists_warn"])
    else:
        CWD_DOT_NOTHING_DIR.mkdir()
        success(glot["made_cwd_dot_nothing_dir"])


@app.command()
def do(procedure_name: str = completable_procedure_name_argument):
    """Go through the steps of a Procedure you have already created"""

    file_location: Path = procedure_location(procedure_name)

    if file_location is None:
        warn_missing_file(procedure_name)
        raise typer.Abort

    procedure: Procedure = deserialize_procedure_file(file_location)

    interactive_walkthrough(procedure)


def _which_procedure(
    which: str,
    title: str,
    description: str,
    destination_dir: Path,
    procedure_filename: str,
) -> Procedure:
    """Wrapper around the logic for deciding what procedure to write when calling
    `not new` with different arguments."""

    path = destination_dir / procedure_filename
    proc_map = {
        "skeleton": Procedure(
            path=path,
            title=glot["skeleton_title"],
            description=glot["skeleton_description"],
            steps=glot["skeleton_steps"],
            context=[glot["skeleton_context_name_name"]],
            knowns=[{glot["skeleton_knowns_name"]: glot["skeleton_knowns_value"]}],
        ),
        "nothing": Procedure(
            path=destination_dir / "nothing.yml",
            title=glot["easter_title"],
            description=glot["easter_description"],
            steps=glot["easter_steps"],
            context=[
                {glot["easter_context_var_name"]: glot["easter_context_var_prompt"]}
            ],
        ),
    }

    return proc_map.get(
        which,
        Procedure(
            path=path,
            title=title,
            description=description,
            steps=glot["steps_placeholder"],
        ),
    )


def _must_be_called_with_name_callback(ctx: typer.Context, value: bool):
    """Ensure that --skeleton and --nothing are always called with --name."""

    empty_called_without_name: bool = (
        ctx.params.get("procedure_name") is None and value is not None
    )

    if empty_called_without_name:
        raise typer.BadParameter(glot["must_be_called_with_name_warn"])

    return value


@app.command(help=glot["new_help"])
def new(
    ctx: typer.Context,
    procedure_name: str = typer.Option(
        None, "--name", "-N", is_eager=True, help=glot["new_procedure_name_option_help"]
    ),
    global_: bool = global_flag,
    skeleton: bool = typer.Option(
        "",
        "--skeleton",
        "-K",
        help=glot["new_skeleton_option_help"],
        flag_value="skeleton",
        callback=_must_be_called_with_name_callback,
    ),
    nothing: bool = typer.Option(
        "", "--nothing", "-T", help=glot["new_nothing_flag_help"], flag_value="nothing"
    ),
    edit_after: bool = edit_after_flag,
    overwrite: bool = typer.Option(
        False, "--overwrite", "-O", help=glot["new_overwrite_option_help"]
    ),
):
    """Subcommand for creating new Procedures"""

    destination_dir = HOME_DOT_NOTHING_DIR if global_ else CWD_DOT_NOTHING_DIR

    prompt_display_defaults = {
        "name": procedure_name,
        "default_destination": friendly_prefix_for_path(destination_dir),
        "edit_after": edit_after,
    }

    # keep ur eye on the ball, there be mutants here
    # _which_procedure() needs these declared no matter what
    title = ""
    description = ""

    if not (skeleton or nothing):
        (
            title,
            description,
            procedure_name,
            destination_dir,
            edit_after,
        ) = prompt_for_new_args(**prompt_display_defaults)

    # just in case the user gave a path with a ~ in it
    destination_dir = Path(destination_dir).expanduser()

    procedure_filename = f"{procedure_name}{PROCEDURE_EXT}"
    procedure = _which_procedure(
        skeleton or nothing,
        title=title,
        description=description,
        destination_dir=destination_dir,
        procedure_filename=procedure_filename,
    )

    try:
        writer.write(procedure, force=overwrite)
    except FileExistsError:
        if confirm_overwrite(procedure.name):
            writer.write(procedure, force=True)

    # pylint: disable=import-outside-toplevel
    if edit_after:
        # this is a special occasion!
        from importlib import reload
        from . import filesystem

        # `state` in filesystem needs to be recalculated on account of the new
        # file in the directories it looks at. importlib does the trick!
        reload(filesystem)

        ctx.invoke(edit, procedure_name=procedure.name)

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
