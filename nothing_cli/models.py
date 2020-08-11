# pylint: disable=too-few-public-methods

"""Pydantic models for Nothing constructs"""
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, validator

from .constants import STEP_SEPARATOR


# pylint: disable= no-self-argument,no-self-use
class Procedure(BaseModel):
    """A Procedure file as a Python object."""

    title: str
    steps: List[str]
    path: Optional[Path] = None
    description: Optional[str] = ""
    context: List[Union[str, Dict]] = []
    knowns: List[Dict] = []

    @validator("steps", pre=True)
    def split_steps(cls, value: str) -> str:
        """Steps come in as a single block of text"""
        return value.split(STEP_SEPARATOR)

    @property
    def name(self):
        """The name of the procedures as understood by the user."""
        return self.path.stem


def context_var_name(context_item: Union[str, Dict]):
    """Handle the fact that an item in the context list can be a string
    or a dictionary. For strings, the variable name is the string. For dicts,
    it's the key name"""

    return (
        context_item
        if isinstance(context_item, str)
        else next(iter(context_item.keys()))
    )
