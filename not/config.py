"""Global and local configuration options"""
from typing import List

from pydantic import BaseSettings


class TaskSpecConfig(BaseSettings):
    """Setting that can be set globally or inside a specific Task Spec file"""

    # content defaults
    title_prefix: str = "Beginning task"
    step_prefix: str = "Step"
    context_prompt: str = "Please provide a value for {}"
    completion_message: str = "All done!"

    # aesthetics
    color: bool = True

    # interaction
    fine_controls: bool = True


class GlobalConfig(TaskSpecConfig):
    """Adds in settings that don't make sense at the individual-spec level"""

    # content defaults
    default_title: str = "Do Nothing"
    default_context_list = [{"name": "What's your name?"}]
    default_presets = [{"apology": "Sorry, {name}. That was cheesy. But it's true!"}]
    default_steps: str = (
        "Take 3 deep breaths, {name}.\n\n"
        "Be still for a moment\n\n"
        "Recall that you are irreplaceable."
    )
    default_steps_expert: str = (
        "Take 3 deep breaths, {name}.\n\n"
        "Be still for a moment\n\n"
        "Recall that you are irreplaceable.\n\n"
        "{apology}"
    )

    # interaction
    editor = str
    edit_on_new: bool = True
    fine_controls: bool = True