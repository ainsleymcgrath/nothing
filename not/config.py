"""Global and local configuration options"""
from pathlib import Path

from pydantic import BaseSettings, Field


class TaskSpecConfig(BaseSettings):
    """Setting that can be set globally or inside a specific Task Spec file.
    The settings that make sense for usage on a specific file."""

    # content defaults
    # XXX this and setting below followed by a colon, prolly put that here
    title_prefix: str = "Beginning task"
    step_prefix: str = "Step"
    # TODO: add validator to make sure this has template
    # TODO: this should be global?
    context_prompt: str = "Please provide a value for {}"
    completion_message: str = "All done!"

    # aesthetics
    color: bool = True

    # interaction
    # XXX probably will not implement


class GlobalConfig(TaskSpecConfig):  # XXX think about inheriting here...
    """Adds in application level settings that don't
    make sense at the individual-spec level"""

    # content defaults
    default_title: str = "Do Nothing"
    default_context_list = [{"name": "What's your name?"}]
    default_presets = [{"apology": "I know hat was cheesy, {name}. But it's true!"}]
    default_steps: str = (
        "Take 3 deep breaths, {name}.\n\n"
        "Find a comfortable position in your seat.\n\n"
        "Begin to breathe lightly and slowly, as if you're going to sleep.\n\n"
        "Close your eyes and count 10 of your gentle breaths."
    )
    default_steps_expert: str = (
        "Take 3 deep breaths, {name}.\n\n"
        "Be still for a moment\n\n"
        "Recall that you are irreplaceable.\n\n"
        "{apology}"
    )

    # commands
    interactive_new: bool = True
    edit_after_write: bool = True
    default_destination_dir: Path = Path.cwd()
