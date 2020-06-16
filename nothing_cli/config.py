# pylint: disable=too-few-public-methods
"""Global and local configuration options"""
import json
import re

from pathlib import Path
from pydantic import BaseSettings, validator
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

from .constants import CONFIG_FILE_NAME, HOME_DOT_NOTHING_DIR
from .localization import polyglot as glot

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


class ProcedureConfig(BaseSettings):
    """Setting that can be set globally or inside a specific Procedure file.
    The settings that make sense for usage on a specific file."""

    step_prefix = glot["step_prefix"]
    context_prompt = glot["context_prompt"]
    completion_message = glot["completion_message"]

    # pylint: disable=no-self-argument, no-self-use
    @validator("context_prompt")  # validators are class methods
    def prompt_must_contain_template(cls, value):
        """The context prompt has context variable names interpolated in,
        so it doesn't work without a place for the interpolation to happen"""

        if not re.search(r"\{.*\}", value):
            raise ValueError

        return value


class GlobalConfig(ProcedureConfig):
    """Adds in application level settings that don't
    make sense at the individual-spec level"""

    default_title = glot["default_title"]
    default_description = glot["default_description"]
    default_context_list = [
        {glot["default_context_name_name"]: glot["default_context_name_prompt"]}
    ]
    # XXX presets not implemented
    default_presets = [{glot["default_presets_name"]: glot["default_presets_response"]}]
    default_steps = glot["default_steps"]

    # commands
    edit_after_write: bool = True
    default_destination_dir: Path = HOME_DOT_NOTHING_DIR

    class Config:  # pylint: disable=missing-docstring
        json_encoders = {Path: lambda p: str(p.resolve())}


def read_global_config_from_file() -> None:
    """Read ~/.nothing/_config.yaml so it can be rolled into a settings instance"""


def write_global_config_to_file() -> None:
    """Used during `not init`, writes ~/.nothing/_config.yaml"""

    config_file = HOME_DOT_NOTHING_DIR / CONFIG_FILE_NAME
    config_values = json.loads(GlobalConfig().json())

    # make steps pretty
    steps_as_scalar_strings = {
        "default_steps": LiteralScalarString(config_values["default_steps"])
    }

    config_file.touch(exist_ok=True)
    yaml.dump({**config_values, **steps_as_scalar_strings}, config_file)
