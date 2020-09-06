# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Tests for `not info`"""

from operator import attrgetter
from pathlib import Path

import pytest

from ...constants import MISSING_INFO_PALCEHOLDER
from ...localization import polyglot as glot
from ...main import app


@pytest.mark.parametrize(
    "field, expected",
    [
        (glot["title_descriptor"], attrgetter("title")),
        (glot["description_descriptor"], MISSING_INFO_PALCEHOLDER),
        (glot["full_path_descriptor"], attrgetter("path")),
        (glot["step_count_descriptor"], "2"),
        (glot["context_vars_descriptor"], MISSING_INFO_PALCEHOLDER),
        (glot["knowns_descriptor"], MISSING_INFO_PALCEHOLDER),
        # no need to test edited/accessed time
    ],
)
def test_basic_all_fields(field, expected, basic_proc: Path, runner):
    result = runner.invoke(app, ["info", basic_proc.name])
    actual = next(
        line.split(":")[-1].lstrip(" ")
        for line in result.output.split("\n")
        if line.startswith(field)
    )
    assert (
        actual == expected if not callable(expected) else expected(basic_proc)
    ), f"{field} provided as expected in info"


@pytest.mark.parametrize(
    "field, expected",
    [
        (glot["title_descriptor"], attrgetter("title")),
        (glot["description_descriptor"], attrgetter("title")),
        (glot["full_path_descriptor"], attrgetter("path")),
        (glot["step_count_descriptor"], "2"),
        (glot["context_vars_descriptor"], attrgetter("context")),
        (glot["knowns_descriptor"], MISSING_INFO_PALCEHOLDER),
        # no need to test edited/accessed time
    ],
)
def test_with_context(field, expected, proc_with_context: Path, runner):
    result = runner.invoke(app, ["info", proc_with_context.name])
    actual = next(
        line.split(":")[-1].lstrip(" ")
        for line in result.output.split("\n")
        if line.startswith(field)
    )
    assert (
        actual == expected if not callable(expected) else expected(proc_with_context)
    ), f"{field} provided as expected in info"


@pytest.mark.parametrize(
    "field, expected",
    [
        (glot["title_descriptor"], attrgetter("title")),
        (glot["description_descriptor"], attrgetter("title")),
        (glot["full_path_descriptor"], attrgetter("path")),
        (glot["step_count_descriptor"], "3"),
        (glot["context_vars_descriptor"], MISSING_INFO_PALCEHOLDER),
        (glot["knowns_descriptor"], "[ what_to_grab=Everything you own ]"),
        # no need to test edited/accessed time
    ],
)
def test_with_knowns(field, expected, proc_with_knowns: Path, runner):
    result = runner.invoke(app, ["info", proc_with_knowns.name])
    actual = next(
        line.split(":")[-1].lstrip(" ")
        for line in result.output.split("\n")
        if line.startswith(field)
    )
    assert (
        actual == expected if not callable(expected) else expected(proc_with_knowns)
    ), f"{field} provided as expected in info"
