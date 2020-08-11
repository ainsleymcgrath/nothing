"""Create Procedure Files from Procedure objects"""
from typing import Dict

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

from .constants import STEP_SEPARATOR
from .localization import polyglot as glot
from .models import Procedure

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def write(procedure: Procedure, force: bool = False):
    """Output the YAML representation of a Procedure object
    to a file in destination_dir"""

    procedure.path.touch(exist_ok=force)

    writable_procedure: Dict = procedure.dict(exclude={"path"}, exclude_defaults=True)
    writable_procedure["steps"] = LiteralScalarString(
        STEP_SEPARATOR.join(step for step in procedure.steps).rstrip()
    )
    yaml.dump(writable_procedure, procedure.path)


def write_easter(destination):
    """Write the cutesy easter egg Procedure"""

    easter_procedure = Procedure(
        path=destination / "nothing.yml",
        title=glot["easter_title"],
        description=glot["easter_description"],
        steps=glot["easter_steps"],
        context=[{glot["easter_context_var_name"]: glot["easter_context_var_prompt"]}],
    )

    write(easter_procedure, force=True)
