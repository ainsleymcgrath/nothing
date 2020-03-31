from typing import Dict, Iterator, List, TypedDict

import yaml

from .utils import task_spec_location


class Step:
    prompt: str
    template_vars: List  # TODO: get vars per step
    number: int

    def __init__(self, prompt, number):
        self.prompt = prompt
        self.number = number


STEP_SEPARATOR = "\n\n"


class TaskSpec:
    title: str
    context_list: List
    steps: Iterator[Step]

    def __init__(self, title: str = "", steps: str = "", context: List = []):
        self.title = title
        self.context_list = context
        self.steps = (
            Step(prompt, i + 1) for i, prompt in enumerate(steps.split(STEP_SEPARATOR))
        )


class TaskSpecDict(TypedDict):
    """When a Nothing yml file is parsed,
    you end up with these top-level dict keys"""

    title: str
    steps: str
    context: List["str"]
    config: Dict = None


def parse(nothingfile_name: str) -> TaskSpec:
    """Take the name of a Nothing spec, try to find it, load into a Nothing"""

    target_file = task_spec_location(nothingfile_name)

    with open(target_file) as f:
        yml: TaskSpecDict = yaml.full_load(f.read())

    return TaskSpec(**yml)
