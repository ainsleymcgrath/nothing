# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name

"""Tests for `not ls`"""

from ...localization import polyglot as glot
from ...main import app


def test_with_files_in_cwd_only(files_in_cwd, runner):
    result = runner.invoke(app, ["ls"])
    assert (
        glot["GLOBAL"] not in result.output
    ), "Global procedures are not shown when they do not exist"

    header, *listed_procedures = [s for s in result.output.split("\n") if s]

    assert glot["LOCAL"] in header
    assert {p.stem for p in files_in_cwd} == {p.lstrip() for p in listed_procedures}


def test_with_files_in_home_only(files_in_home, runner):
    result = runner.invoke(app, ["ls"])
    assert (
        glot["LOCAL"] not in result.output
    ), "Local procedures are not shown when they do not exist"

    header, *listed_procedures = [s for s in result.output.split("\n") if s]

    assert glot["GLOBAL"] in header
    assert {p.stem for p in files_in_home} == {p.lstrip() for p in listed_procedures}


def test_with_files_existing_both_places(files_in_cwd_and_home, runner):
    result = runner.invoke(app, ["ls"])

    assert (
        glot["LOCAL"] in result.output and glot["GLOBAL"] in result.output
    ), "Local procedures are not shown when they do not exist"
