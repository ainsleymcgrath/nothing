# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test suite for `not do`.
When you see CliRunner.invoke called with `input=[...]`,
know that the newlines are often the user 'pressing enter to continue'
during a procedure.  """

from pathlib import Path

from ...main import app
from ...models import context_var_name


def test_successful_run(basic_proc: Path, runner):
    result = runner.invoke(app, ["do", basic_proc.name], input="\n\n")

    assert not result.exception
    assert "It doesn't look like there's a procedure" not in result.output
    assert basic_proc.title in result.output


def test_nonexistent_proc(runner):
    result = runner.invoke(app, ["do", "flim-flam-kazam"])

    assert (
        "It doesn't look like there's a procedure for 'flim-flam-kazam'"
        in result.output
    )


def test_with_context(proc_with_context: Path, runner):
    result = runner.invoke(
        app, ["do", proc_with_context.name], input="carrots\ncelery\n" + "\n\n"
    )
    _, step_1, step_2 = result.output.split("Step")

    assert not any(
        context_var_name(c) in step
        for c in proc_with_context.context
        for step in [step_1, step_2]
    ), "The names of the context variables don't make it into the final output"


def test_with_lazy_context(proc_with_lazy_context: Path, runner):
    result = runner.invoke(
        app, ["do", proc_with_lazy_context.name], input="\n" + "5:00" + "\n\n"
    )
    [
        # well, this is where the prompts _would_ be. there are none in this case
        marquis_and_initial_prompts,
        _,
        step_2,  # this is where the lazy var shows up
        _,
    ] = result.output.split("Step")

    lazy_context_prompt = next(iter(proc_with_lazy_context.context[0].values()))

    assert (
        lazy_context_prompt not in marquis_and_initial_prompts
    ), "The lazy context variable is not prompted for at the start"

    assert (
        "5:00" in step_2
    ), "The lazy context variable does get interpolated when the time is right"


def test_with_knowns(proc_with_knowns: Path, runner):
    result = runner.invoke(app, ["do", proc_with_knowns.name], input="\n\n\n")
    _, _, step_2, _ = result.output.split("Step")
    known_value = next(iter(proc_with_knowns.knowns[0].values()))

    assert known_value in step_2
