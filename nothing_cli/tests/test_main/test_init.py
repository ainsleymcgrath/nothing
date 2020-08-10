# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test suite for `not init`"""
from pathlib import Path

import pytest

from ...localization import polyglot as glot
from ...main import app


@pytest.fixture
def filesystem_is_patched_but_cwd_dot_nothing_dir_not_exists(
    existing_cwd_dot_nothing_dir: Path,
) -> Path:
    """The included fixture patches CWD_DOT_NOTHING_DIR."""
    existing_cwd_dot_nothing_dir.rmdir()
    return existing_cwd_dot_nothing_dir


def test_dir_not_exists(
    filesystem_is_patched_but_cwd_dot_nothing_dir_not_exists, runner
):
    result = runner.invoke(app, ["init"])

    assert (
        glot["made_cwd_dot_nothing_dir"] in result.output
    ), "Cwd dot nothing dir created when not exists"


def test_cwd_dot_nothing_already_exists(existing_home_dot_nothing_dir, runner):
    result = runner.invoke(app, ["init"])

    assert (
        glot["cwd_dot_nothing_exists_warn"] in result.output
    ), "Warning emitted when CWD dot nothing already exists"


# def test_home_dot_nothing_not_exists(only_cwd_dot_nothing_exists: Path, runner):
# assert 0
