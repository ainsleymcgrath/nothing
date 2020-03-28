from typing import Iterator, List, TypedDict

from pathlib import Path

import yaml


class Step:
    prompt: str
    template_vars: List  # TODO: get vars per step
    number: int

    def __init__(self, prompt, number):
        self.prompt = prompt
        self.number = number


STEP_SEPARATOR = "\n\n"


class Nothing:
    title: str
    context_list: List
    steps: Iterator[Step]

    def __init__(self, title: str = "", steps: str = "", context: List = []):
        self.title = title
        self.context_list = context
        self.steps = (
            Step(prompt, i + 1) for i, prompt in enumerate(steps.split(STEP_SEPARATOR))
        )


class NothingFileDict(TypedDict):
    """When a Nothing yml file is parsed,
    you end up with these top-level dict keys"""

    title: str
    steps: str
    context: List["str"]


def parse(file: str) -> Nothing:
    """Take the name of a Nothing spec, try to find it, load into a Nothing"""

    # TODO: expect yaml also
    # TODO: search for local .nothings/{file}, then global, then parents of local
    with open(f"{file}.yml") as f:
        yml: NothingFileDict = yaml.full_load(f.read())

    return Nothing(**yml)
