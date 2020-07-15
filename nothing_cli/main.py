# pylint: disable=too-many-arguments

"""The subcommands of `not`"""
from pathlib import Path

import typer

from . import writer
from .completions import procedure_name_completions
from .constants import (
    CWD_DOT_NOTHING_DIR,
    DirectoryChoicesForListCommand,
    HOME_DOT_NOTHING_DIR,
    ValidExtensions,
)
from .filesystem import (
    deserialize_procedure_file,
    friendly_prefix_for_path,
    path_to_write_to,
    procedure_location,
)
from .localization import polyglot as glot
from .models import Procedure, ProcedureCreate
from .theatrics import (
    ask,
    confirm_drop,
    confirm_overwrite,
    interactive_walkthrough,
    warn_missing_file,
    prompt_for_copy_args,
    prompt_for_new_args,
    config_exists_warn,
    show_dossier,
    show_fancy_list,
    success,
)


app = typer.Typer(help=glot["help"])

completable_procedure_name_argument: typer.Argument = typer.Argument(
    str, autocompletion=procedure_name_completions
)


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
        return

    with file_location.open() as file:
        procedure: Procedure = deserialize_procedure_file(file.read())

    interactive_walkthrough(procedure)


def empty_callback(ctx: typer.Context, value: bool):
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
    extension: ValidExtensions = typer.Option(
        ValidExtensions.yml,
        "--extension",
        "-X",
        help=glot["new_extension_option_help"],
        show_default=True,
    ),
    global_: bool = typer.Option(
        False, "--global", "-G", help=glot["new_global_option_help"]
    ),
    empty: bool = typer.Option(
        False,
        "--empty",
        "-E",
        callback=empty_callback,
        help=glot["new_empty_option_help"],
    ),
    edit_after: bool = typer.Option(
        True, "--edit-after", "-A", help=glot["new_edit_after_option_help"]
    ),
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
            "default_extension": extension,
            "default_destination": friendly_prefix_for_path(destination_dir),
            "edit_after_write": edit_after,
        }

        (
            title,
            description,
            procedure_name,
            extension,
            destination_dir,
            edit_after,
        ) = prompt_for_new_args(**defaults)
        # just in case the user gave a path with a ~ in it
        destination_dir = Path(destination_dir).expanduser()

    procedure_filename = f"{procedure_name}.{extension}"
    if empty:
        procedure = ProcedureCreate(filename=procedure_filename)

    else:
        procedure = ProcedureCreate(
            title=title, description=description, filename=procedure_filename
        )

    try:
        writer.write(procedure, destination_dir, force=overwrite)
    except FileExistsError:
        if confirm_overwrite(procedure_name):
            writer.write(procedure, destination_dir, force=True)

    if edit_after:
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
    """Edit existing Procedure"""
    path_to_procedure: Path = procedure_location(procedure_name).resolve()

    if rename:
        new_name = ask(glot["filename_prompt"])
        path_to_procedure.rename(path_to_procedure.parent / new_name)

    typer.edit(filename=str(path_to_procedure))
    success(glot.localized("file_edited", {"name": "procedure_name"}))


@app.command()
def copy(  # XXX these defaults are wack
    ctx: typer.Context,
    existing_procedure_name: str = completable_procedure_name_argument,
    new_procedure_name=typer.Argument(None),
    new_title: str = None,
    destination_dir: Path = None,
    new_extension: ValidExtensions = None,
    edit_after_write: bool = False,
):
    """Copy an old Procedure to a new one with the provided name"""

    original_file: Path = procedure_location(existing_procedure_name)

    if original_file is None:
        warn_missing_file(existing_procedure_name)
        return

    old_procedure: Procedure = deserialize_procedure_file(original_file)
    interactive = existing_procedure_name is not None or new_procedure_name is not None

    if interactive:
        extension_without_dot = original_file.suffix.lstrip(".")
        defaults = {
            "default_title": old_procedure.title,
            "default_destination": friendly_prefix_for_path(original_file.parent),
            "default_extension": extension_without_dot,
            "edit_after_write": edit_after_write,
        }
        # just in case the user gave a path with a ~ in it
        destination_dir = Path(destination_dir).expanduser()

        (
            new_procedure_name,
            new_title,
            destination_dir,
            new_extension,
            edit_after_write,
        ) = prompt_for_copy_args(**defaults)

    new_filename = f"{new_procedure_name}.{new_extension}"
    new_procedure: Procedure = old_procedure.copy(
        update={"filename": new_filename, "title": new_title}
    )

    try:
        writer.write(new_procedure, destination_dir.expanduser())
    except FileExistsError:
        if confirm_overwrite(new_procedure_name):
            writer.write(new_procedure, destination_dir.expanduser(), force=True)

    if edit_after_write:
        ctx.invoke(edit, procedure_name=new_procedure_name)

    success(
        glot.localized(
            "copied",
            {"name": existing_procedure_name, "destination": destination_dir.resolve()},
        )
    )


@app.command()
def ls(include: DirectoryChoicesForListCommand = DirectoryChoicesForListCommand.both):
    """Display the location of every Procedure in cwd and/or $HOME"""

    show_fancy_list(include)


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
