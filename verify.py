"""Version sanity check"""

from pathlib import Path
from sys import exit

from nothing_cli import __version__

pyproject_toml_version: str = next(
    line.split(" = ")[1].rstrip("\n").lstrip('"').rstrip('"')
    for line in Path("pyproject.toml").open().readlines()
    if line.startswith("version = ")
)

if __version__ != pyproject_toml_version:
    exit("Mismatched versions. Edit pyproject.toml or nothing_cli.__version__")

print("Ok")
