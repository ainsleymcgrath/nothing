from typing import Dict

from .parser_ import TaskSpec, Step
from .theatrics import spacious_print, dramatic_title

import typer


def run(nothing: TaskSpec):
    dramatic_title(f"Doing nothing: {nothing.title}")

    context_dict = {}

    if nothing.context_list:
        for context_var in nothing.context_list:
            context_value = typer.prompt(f"Please provide a value for {context_var}")
            context_dict[context_var] = context_value

    typer.echo()
    for step in nothing.steps:
        run_step(step, context_dict)

    typer.echo("All done!")


def run_step(step: Step, context: Dict):
    typer.echo(f"Step {step.number}:")

    try:
        spacious_print(step.prompt.format(**context))
    except KeyError:
        spacious_print(step.prompt)

    # TODO: rather than enter, prompt for:
    # [n]ext, [p]revious, [r]estart, or [q]uit
    input("Press enter to continue...")
    typer.echo()
