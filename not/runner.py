"""Walk through a Task Spec interactively"""
from typing import Dict

import typer

from .models import Step, TaskSpec
from .config import GlobalConfig
from .theatrics import spacious_print, dramatic_title


config = GlobalConfig()


def run(task_spec: TaskSpec):
    """Interactively walk through a task spec"""
    # TODO: merge in spec-level config...

    dramatic_title(f"{config.title_prefix}: {task_spec.title}")

    context_dict = {}

    if task_spec.context:
        for item in task_spec.context:
            context_value = typer.prompt(item.prompt)
            context_dict[item.var_name] = context_value

    typer.echo()
    for i, step in enumerate(task_spec.steps):
        run_step(step, context_dict, number=i)

    typer.echo(config.completion_message)


def run_step(step: Step, context: Dict, number=None):
    """Run just one Step in a TaskSpec"""
    typer.echo(f"{config.step_prefix} {step.number}:")

    try:
        spacious_print(step.prompt.format(**context))
    except KeyError:
        spacious_print(step.prompt)

    # TODO: rather than enter, prompt for:
    # [n]ext, [p]revious, [r]estart, or [q]uit
    input("Press enter to continue...")
    typer.echo()
