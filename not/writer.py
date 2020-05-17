"""Create Task Spec Files from TaskSpec objects"""
from typing import Dict, List, Union
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

from .constants import FIELD_NAMES_EXCLUDED_FROM_CLEANED_TASK_SPEC, STEP_SEPARATOR
from .models import TaskSpec


yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def write(task_spec: TaskSpec, destination_dir: Path, force: bool = False):
    """Output the YAML representation of a TaskSpec object
    to a file in destination_dir"""

    file_path: Path = destination_dir / task_spec.filename
    file_path.touch(exist_ok=force)

    writable_task_spec: Dict = clean(task_spec)

    yaml.dump(writable_task_spec, file_path)


def clean(task_spec: TaskSpec) -> Dict:
    """Strip unnecessary fields and serialize non-primitive ones to create
    a dict that a user would like to see in a Task Spec file"""

    unset_fields = (field for field, value in task_spec.dict().items() if value is None)
    exclusions = (*FIELD_NAMES_EXCLUDED_FROM_CLEANED_TASK_SPEC, *unset_fields)

    task_spec_sans_exclusions: Dict = {
        k: v for k, v in task_spec.dict().items() if k not in exclusions
    }
    steps_as_literal_scalar_string: Dict = {
        "steps": LiteralScalarString(
            STEP_SEPARATOR.join(step.prompt for step in task_spec.steps).rstrip()
        )
    }
    context_as_list_of_mappings: Dict[str, List[Union[Dict, str]]] = {
        "context": [
            {item.var_name: item.prompt} if item.is_complex else item.var_name
            for item in task_spec.context
        ]
    }

    return {
        **task_spec_sans_exclusions,
        **steps_as_literal_scalar_string,
        **context_as_list_of_mappings,
    }
