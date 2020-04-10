"""Entry point to serialize Task Spec files to TaskSpec objects"""
from typing import Dict, List
from ruamel.yaml import YAML

from .models import (
    ContextItem,
    context_items_from_yaml,
    Step,
    steps_from_yaml_block,
    TaskSpec,
    TaskSpecInspection,
)

yaml = YAML()


def serialize_task_spec_file(task_spec_content: str) -> TaskSpec:
    """Take the content of a Task Spec file, try to find the corresponding file,
    return it as a TaskSpec object"""

    yml: Dict = yaml.load(task_spec_content)

    raw_steps = yml.pop("steps")
    raw_context = yml.pop("context", None)

    parsed_steps: List[Step] = steps_from_yaml_block(raw_steps)
    parsed_context: List[ContextItem] = context_items_from_yaml(raw_context)

    return TaskSpec(steps=parsed_steps, context=parsed_context, **yml)


def inspect(task_spec: TaskSpec) -> TaskSpecInspection:
    pass
