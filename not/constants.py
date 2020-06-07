"""Unchanging values that would be inappropriate for config"""
from enum import Enum
import re
from typing import List, Set

from .localization import polyglot as glot

VALID_TASK_SPEC_EXTENSION_NAMES: List = ["yml", "yaml", "not"]
DOT_NOTHING_DIRECTORY_NAME: str = ".nothing"
STEP_SEPARATOR: str = "\n\n"
TASK_SPEC_EXT_PATTERN = re.compile(r"(\.not|\.yml|\.yaml)$")

FIELD_NAMES_EXCLUDED_FROM_CLEANED_TASK_SPEC: Set = {"filename"}


class DirectoryChoicesForListCommand(str, Enum):
    cwd = glot["cwd"]
    home = glot["home"]
    both = glot["both"]
