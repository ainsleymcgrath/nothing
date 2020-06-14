"""Create Procedure Files from Procedure objects"""
from typing import Dict, List, Union
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

from .constants import FIELD_NAMES_EXCLUDED_FROM_CLEANED_PROCEDURE, STEP_SEPARATOR
from .models import Procedure


yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def write(procedure: Procedure, destination_dir: Path, force: bool = False):
    """Output the YAML representation of a Procedure object
    to a file in destination_dir"""

    file_path: Path = destination_dir / procedure.filename
    file_path.touch(exist_ok=force)

    writable_procedure: Dict = clean(procedure)

    yaml.dump(writable_procedure, file_path)


def clean(procedure: Procedure) -> Dict:
    """Strip unnecessary fields and serialize non-primitive ones to create
    a dict that a user would like to see in a Procedure file"""

    unset_fields = (field for field, value in procedure.dict().items() if value is None)
    exclusions = (*FIELD_NAMES_EXCLUDED_FROM_CLEANED_PROCEDURE, *unset_fields)

    procedure_sans_exclusions: Dict = {
        k: v for k, v in procedure.dict().items() if k not in exclusions
    }
    steps_as_literal_scalar_string: Dict = {
        "steps": LiteralScalarString(
            STEP_SEPARATOR.join(step.prompt for step in procedure.steps).rstrip()
        )
    }
    context_as_list_of_mappings: Dict[str, List[Union[Dict, str]]] = {
        "context": [
            {item.var_name: item.prompt} if item.is_complex else item.var_name
            for item in procedure.context
        ]
    }

    return {
        **procedure_sans_exclusions,
        **steps_as_literal_scalar_string,
        **context_as_list_of_mappings,
    }
