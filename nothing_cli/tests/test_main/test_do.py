# pylint: disable=missing-function-docstring,unused-argument,invalid-name
"""Test suite for `not do`"""
import pytest

from ...main import app
from ...models import ProcedureCreate, Step
from ...writer import write


@pytest.fixture
def proc(cwd_dot_nothing_dir_exists):
    steps_for_procedure = [
        Step(prompt=prompt, number=i)
        for i, prompt in enumerate(["Get ready!", "Do the thing."])
    ]

    _proc = ProcedureCreate(
        filename="do-the-thing.yml",
        title="Do The Thing",
        description="How to do the thing",
        steps=steps_for_procedure,
        knowns=[],
        context=[],
    )

    write(_proc, cwd_dot_nothing_dir_exists)

    return _proc


def test_successful_run(runner, proc):
    result = runner.invoke(app, ["do", proc.name], input="\n\n")

    assert not result.exception
    assert "Aborted" not in result.output
    assert proc.title in result.output
    assert proc.description in result.output


def test_nonexistent_proc(runner):
    result = runner.invoke(app, ["do", "flim-flam-kazam"])

    assert (
        "It doesn't look like there's a procedure for 'flim-flam-kazam'"
        in result.output
    )
