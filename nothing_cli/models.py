"""Pydantic models for Nothing constructs"""
from typing import Dict, List, Union
from pydantic import BaseModel

from .constants import STEP_SEPARATOR
from .localization import polyglot as glot


class Step(BaseModel):
    """A step within a procedure.

    self.template vars is a list of the kwargs needed to format self.prompt"""

    prompt: str
    template_vars: List = []  # TODO: get vars per step
    number: int


def steps_from_yaml_block(raw_steps: str) -> List[Step]:
    """Takes the string from a yaml block-scalar
    and return it as a list of Step objects"""

    return [
        Step(prompt=prompt, number=i + 1)
        for i, prompt in enumerate(raw_steps.split(STEP_SEPARATOR))
    ]


class ContextItem(BaseModel):
    """A member of the `context` list"""

    var_name: str
    prompt: str = glot["context_prompt"]

    @property
    def is_complex(self):
        """In a Procedure file, if a context item is denoted as a mapping,
        then it is considered "complex"""

        return self.prompt != glot["context_prompt"].format(self.var_name)


def context_items_from_yaml_list(
    raw_context: Union[List[str], List[Dict], None]
) -> List[ContextItem]:
    """Takes a list extracted from yaml and
    returns it as a list of ContextItem objects"""

    if raw_context is None:
        return None

    def _from_simple(context_item: str):
        """Interpolate the literal_var_name into the configured context prompt"""
        interpolated_prompt = glot["context_prompt"].format(context_item)
        return ContextItem(var_name=context_item, prompt=interpolated_prompt)

    def _from_complex(context_item: Dict):
        # TODO: bad docstring
        """The dictionary key serves as the var name. The value serves as the prompt."""
        var_name, prompt = next(iter(context_item.items()))
        return ContextItem(var_name=var_name, prompt=prompt)

    return [
        _from_simple(context_item)
        if isinstance(context_item, str)
        else _from_complex(context_item)
        for context_item in raw_context
    ]


class Procedure(BaseModel):
    """A Procedure file as a Python object.
    Can be initialized without filename since it's mostly
    here for deserializating spec files"""

    filename: str = None
    title: str
    description: str = None
    steps: List[Step]
    context: List[ContextItem] = None
    presets: List[Dict] = None


class ProcedureCreate(Procedure):
    """Serializeable to a basic Procedure file, the default for `not new`"""

    filename: str
    title = glot["default_title"]
    description = glot["default_description"]
    steps: List[Step] = steps_from_yaml_block(glot["default_steps"])
    context: List[ContextItem] = context_items_from_yaml_list(
        [{glot["default_context_name_name"]: glot["default_context_name_prompt"]}]
    )


# TODO deprecate
class ProcedureCreateExpert(Procedure):
    """Serializeable to a Procedure file with all optional keys exposed"""

    filename: str
    # XXX presets not implemented
    # presets: List[Dict]
