# pylint: disable=missing-class-docstring

"""Unchanging values that would be inappropriate for config"""
from enum import Enum
from pathlib import Path
import re
from typing import List, Set

from .localization import polyglot as glot


class ValidExtensions(str, Enum):
    yml = "yml"
    yaml = "yaml"


VALID_PROCEDURE_EXTENSION_NAMES: List = [e.value for e in ValidExtensions]
DOT_NOTHING_DIRECTORY_NAME: str = ".nothing"
STEP_SEPARATOR: str = "\n\n"
PROCEDURE_EXT_PATTERN = re.compile(r"(\.yml|\.yaml)$")
LAZY_CONTEXT_PREFIX = "__"

CWD: Path = Path.cwd()
HOME: Path = Path.home()

DOT_NOTHING_DIRECTORY_NAME: str = ".nothing"
CWD_DOT_NOTHING_DIR: Path = CWD / DOT_NOTHING_DIRECTORY_NAME
HOME_DOT_NOTHING_DIR: Path = HOME / DOT_NOTHING_DIRECTORY_NAME

FIELD_NAMES_EXCLUDED_FROM_CLEANED_PROCEDURE: Set = {"filename"}


class DirectoryChoicesForListCommand(str, Enum):
    cwd = glot["cwd"]
    home = glot["home"]
    both = glot["both"]
