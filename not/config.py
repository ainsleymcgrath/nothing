"""Global and local configuration options"""
from pathlib import Path
from pydantic import BaseSettings

from .constants import HOME_DOT_NOTHING_DIR
from .localization import polyglot as glot


class TaskSpecConfig(BaseSettings):
    """Setting that can be set globally or inside a specific Task Spec file.
    The settings that make sense for usage on a specific file."""

    # content defaults
    # XXX this and setting below followed by a colon, prolly put that here
    title_prefix = glot["title_prefix"]
    step_prefix = glot["step_prefix"]
    # TODO: add validator to make sure this has template
    # TODO: this should be global?
    context_prompt = glot["context_prompt"]
    completion_message = glot["completion_message"]

    # aesthetics
    color: bool = True

    # interaction
    # XXX probably will not implement


class GlobalConfig(TaskSpecConfig):  # XXX think about inheriting here...
    """Adds in application level settings that don't
    make sense at the individual-spec level"""

    # content defaults
    default_title = glot["default_title"]
    default_description = glot["default_description"]
    default_context_list = [
        {glot["default_context_name_name"]: glot["default_context_name_prompt"]}
    ]
    default_presets = [{glot["default_presets_name"]: glot["default_presets_response"]}]
    default_steps = glot["default_steps"]
    default_steps_expert = glot["default_steps_expert"]

    # commands
    interactive_new: bool = True
    edit_after_write: bool = True
    default_destination_dir: Path = HOME_DOT_NOTHING_DIR
