# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test suite for `not do`"""
from pathlib import Path
from typing import List

# import these constants from filesystem because they're patched there
from ...filesystem import CWD_DOT_NOTHING_DIR, HOME_DOT_NOTHING_DIR
from ...main import app


def test_file_exist(files_in_cwd_and_home: List[Path], runner):
    cwd_file = files_in_cwd_and_home[0]
    home_file = files_in_cwd_and_home[-1]

    result1 = runner.invoke(app, ["drop", cwd_file.stem], input="yes\n")
    result2 = runner.invoke(app, ["drop", home_file.stem], input="yes\n")

    assert "Success" in result1.output
    assert "Success" in result2.output

    assert not any(file.name == cwd_file.name for file in CWD_DOT_NOTHING_DIR.glob("*"))
    assert not any(
        file.name == home_file.name for file in HOME_DOT_NOTHING_DIR.glob("*")
    )


def test_no_confirm(files_in_cwd: List[Path], runner):
    cwd_file = files_in_cwd[0]
    result = runner.invoke(app, ["drop", cwd_file.stem, "--no-confirm"])

    assert "Success" in result.output


def test_file_not_exists(runner):
    result = runner.invoke(app, ["drop", "what??"], input="yes\n")

    assert "Aborted" in result.output
