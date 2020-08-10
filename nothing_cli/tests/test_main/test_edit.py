# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test suite for `not edit`"""
import pytest

from ...localization import polyglot as glot
from ...main import app, typer


@pytest.fixture(autouse=True)
def mock_typer_edit(monkeypatch):
    def mock_edit(*args, filename=None, **kwargs):
        """Raises an exception if given a falsey name, since the normal
        behavior of typer.edit would be to freak out if no file existed"""

        if not filename:
            raise ValueError

    monkeypatch.setattr(typer, "edit", mock_edit)


def test_file_exists(runner, files_in_home):
    result = runner.invoke(app, ["edit", files_in_home[0].stem])

    assert glot["stylish_interjection"] in result.output
    assert files_in_home[0].stem in result.output


def test_file_not_exists(runner):
    result = runner.invoke(app, ["edit", "pirate ship!"])

    assert glot["missing_file_warn"].format(name="pirate ship!") in result.output
    assert isinstance(result.exception, SystemExit)


def test_rename(runner, files_in_home):
    result = runner.invoke(
        app, ["edit", files_in_home[1].stem, "--rename"], input="jacob\n"
    )

    assert glot["stylish_interjection"] in result.output
    assert (
        glot["file_renamed"].format(old_name=files_in_home[1].stem, name="jacob")
        in result.output
    )
