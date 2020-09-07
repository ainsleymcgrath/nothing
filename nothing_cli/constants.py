# pylint: disable=missing-class-docstring

"""Unchanging values that would be inappropriate for config"""
from pathlib import Path

VERSION: str = next(
    line.split(" = ")[1].rstrip("\n").lstrip('"').rstrip('"')
    for line in Path("pyproject.toml").open().readlines()
    if line.startswith("version = ")
)

STEP_SEPARATOR: str = "\n\n"
PROCEDURE_EXT: str = ".yml"
PROCEDURE_EXT_GLOB: str = r".y[am]l"  # allow 'yaml' for that 1 roll-your-own weirdo
LAZY_CONTEXT_PREFIX: str = "__"
MISSING_INFO_PALCEHOLDER = "-"

CWD: Path = Path.cwd()
HOME: Path = Path.home()

DOT_NOTHING_DIRECTORY_NAME: str = ".nothing"
CWD_DOT_NOTHING_DIR: Path = CWD / DOT_NOTHING_DIRECTORY_NAME
HOME_DOT_NOTHING_DIR: Path = HOME / DOT_NOTHING_DIRECTORY_NAME
