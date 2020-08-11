# pylint: disable=missing-class-docstring

"""Unchanging values that would be inappropriate for config"""
from enum import Enum
from pathlib import Path


class ValidExtensions(str, Enum):
    yml = "yml"
    yaml = "yaml"


STEP_SEPARATOR: str = "\n\n"
PROCEDURE_EXT = ".yml"
PROCEDURE_EXT_GLOB = r".y[am]l"  # allow yaml for that one roll-your-own-proc weirdo
LAZY_CONTEXT_PREFIX = "__"

CWD: Path = Path.cwd()
HOME: Path = Path.home()

DOT_NOTHING_DIRECTORY_NAME: str = ".nothing"
CWD_DOT_NOTHING_DIR: Path = CWD / DOT_NOTHING_DIRECTORY_NAME
HOME_DOT_NOTHING_DIR: Path = HOME / DOT_NOTHING_DIRECTORY_NAME
