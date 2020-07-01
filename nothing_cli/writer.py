"""Create Procedure Files from Procedure objects"""
from typing import Dict, List, Union
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

from .constants import FIELD_NAMES_EXCLUDED_FROM_CLEANED_PROCEDURE, STEP_SEPARATOR
from .localization import polyglot as glot
from .models import context_items_from_yaml_list, Procedure, steps_from_yaml_block


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
        **procedure.dict(exclude=FIELD_NAMES_EXCLUDED_FROM_CLEANED_PROCEDURE),
        **steps_as_literal_scalar_string,
        **context_as_list_of_mappings,
    }


def write_easter(destination):
    """Write the cutesy easter egg Procedure"""

    easter_procedure = Procedure(
        filename="nothing.yml",
        title=glot["easter_title"],
        description=glot["easter_description"],
        steps=steps_from_yaml_block(glot["easter_steps"]),
        context=context_items_from_yaml_list(
            {glot["easter_context_var_name"]: glot["easter_context_var_prompt"]}
        ),
    )

    write(easter_procedure, destination, force=True)
