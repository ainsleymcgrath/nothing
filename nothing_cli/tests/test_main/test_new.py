# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test fixtures for `not new`"""

from typing import NamedTuple
from unittest.mock import Mock

import pytest
import typer
from slugify import slugify

from ... import main
from ...filesystem import deserialize_procedure_file
from ...localization import polyglot as glot
from ...main import app
from ...models import Procedure


@pytest.fixture(autouse=True)
def tweaked_pathlib(existing_cwd_dot_nothing_dir, monkeypatch):
    """The `new` subcommand calls Path() directly on the destination dir name, so the
    autouse fixtures in the top level conftest don't apply here."""

    with monkeypatch.context() as m:
        # use the context manager to be extra cautious when patching stdlib
        m.setattr(main, "Path", lambda *_: existing_cwd_dot_nothing_dir)
        yield


@pytest.fixture
def patched_typer_edit(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(typer, "edit", mock)
    return mock


RETURN = "\n"


class _NothingCLIInputs(NamedTuple):
    """The prompts a user can respond to for `not new` in order"""

    title: str
    description: str = ""
    filename: str = ""
    destination: str = ""
    edit: str = ""


@pytest.fixture
def user_accepts_all_defaults():
    return _NothingCLIInputs(title="Nice")


def test_with_no_options_accept_all_defaults(
    user_accepts_all_defaults, patched_typer_edit, existing_cwd_dot_nothing_dir, runner
):
    result = runner.invoke(app, ["new"], input=RETURN.join(user_accepts_all_defaults))

    assert result.exit_code == 0
    assert not result.exception
    assert patched_typer_edit.called, "Editor is opened when defaults accepted"

    created_file = next(
        existing_cwd_dot_nothing_dir.glob(
            f"*{slugify( user_accepts_all_defaults.title )}*"
        )
    )

    assert created_file.exists()

    proc: Procedure = deserialize_procedure_file(created_file)

    assert user_accepts_all_defaults.title == proc.title
    assert not proc.context, "Context not included in empty procedure"
    assert not proc.knowns, "Knowns not included in empty procedure"
    assert len(proc.steps) == 1
    assert proc.steps[0] == glot["steps_placeholder"].rstrip("\n")


@pytest.fixture
def user_accepts_no_defaults() -> _NothingCLIInputs:
    return _NothingCLIInputs(
        title="finding nemo", description="Find dat boi", destination="home", edit="no"
    )


def test_with_no_options_accept_no_defaults(
    user_accepts_no_defaults, patched_typer_edit, existing_cwd_dot_nothing_dir, runner
):
    result = runner.invoke(app, ["new"], input=RETURN.join(user_accepts_no_defaults))

    assert result.exit_code == 0
    assert not result.exception
    assert (
        not patched_typer_edit.called
    ), "When user answers no to edit prompt, editor not opened"

    created_file = next(
        existing_cwd_dot_nothing_dir.glob(
            f"*{slugify(user_accepts_no_defaults.title)}*"
        )
    )

    assert created_file.exists()

    proc: Procedure = deserialize_procedure_file(created_file)

    assert user_accepts_no_defaults.title == proc.title
    assert not proc.context, "Context not included in empty procedure"
    assert not proc.knowns, "Knowns not included in empty procedure"
    assert len(proc.steps) == 1
    assert proc.steps[0] == glot["steps_placeholder"].rstrip("\n")


@pytest.mark.parametrize("flag_variant", ["--skeleton", "-K"])
def test_skeleton(existing_cwd_dot_nothing_dir, runner, flag_variant):
    proc_name = "how-to-dance"
    result = runner.invoke(app, ["new", "-N", proc_name, "--no-edit", flag_variant])

    assert result.exit_code == 0
    assert not result.exception

    created_file = next(existing_cwd_dot_nothing_dir.glob(f"*{proc_name}*"))

    assert created_file.exists()


@pytest.mark.parametrize("flag_variant", ["--nothing", "-T"])
def test_nothing(existing_cwd_dot_nothing_dir, runner, flag_variant):
    result = runner.invoke(app, ["new", "--no-edit", flag_variant])
    assert result.exit_code == 0
    assert not result.exception

    created_file = next(existing_cwd_dot_nothing_dir.glob("nothing.yml"))

    assert created_file.exists()


@pytest.mark.parametrize("option", ["--skeleton", "-K"])
def test_options_that_require_name(runner, option):
    result = runner.invoke(app, ["new", option])

    assert result.exit_code != 0, f"Command fails when {option} given without --name"
    assert glot["must_be_called_with_name_warn"] in result.output


@pytest.fixture
def preexisting_proc(existing_cwd_dot_nothing_dir):
    proc = existing_cwd_dot_nothing_dir / "lol.yml"
    proc.touch()
    return proc


def test_attempt_overwrite_without_flag(preexisting_proc, runner):

    result = runner.invoke(
        app, ["new", "--name", preexisting_proc.stem, "--no-edit", "-K"]
    )
    assert glot["overwrite_warn"].format(name=preexisting_proc.stem) in result.output


@pytest.mark.parametrize("flag_variant", ["--overwrite", "-O"])
def test_with_overwrite_flag(preexisting_proc, runner, flag_variant):

    result = runner.invoke(
        app, ["new", "--name", preexisting_proc.stem, "--no-edit", "-K", flag_variant]
    )
    assert (
        glot["overwrite_warn"].format(name=preexisting_proc.stem) not in result.output
    ), "No warning prompt is given"

    assert result.exit_code == 0
    assert glot["stylish_interjection"] in result.output
