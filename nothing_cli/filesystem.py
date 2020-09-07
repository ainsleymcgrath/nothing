"""filesystem utilities for not"""
from collections import defaultdict
from os.path import getatime, getmtime
from pathlib import Path
from time import ctime
from typing import Callable, Dict, Iterator, List, Optional, Tuple, Union

from ruamel.yaml import YAML
from typer import Abort, echo

from .constants import (
    CWD,
    CWD_DOT_NOTHING_DIR,
    HOME,
    HOME_DOT_NOTHING_DIR,
    PROCEDURE_EXT,
    PROCEDURE_EXT_GLOB,
)
from .localization import polyglot as glot
from .models import Procedure, context_var_name

yml = YAML()  # singleton pls


def initstate() -> Callable[[Optional[bool]], Union[Iterator[Path], List[Path]]]:
    """For the lifecycle of any subcommands that read from the filesytem,
    application state can be defined as the collection of .yml files in home and cwd"""

    if not CWD_DOT_NOTHING_DIR.exists() and not HOME_DOT_NOTHING_DIR.exists():
        echo(glot["missing_dot_nothings_warn"])

        raise Abort

    existing_procedures: Tuple[Path] = (
        *CWD_DOT_NOTHING_DIR.glob(f"*{PROCEDURE_EXT_GLOB}"),
        *HOME_DOT_NOTHING_DIR.glob(f"*{PROCEDURE_EXT_GLOB}"),
    )

    def _state(iterator=False) -> Union[Iterator[Path], List[Path]]:
        return iter(existing_procedures) if iterator else existing_procedures

    return _state


state: Callable[[Optional[bool]], Union[List, Iterator]] = initstate()


# pylint: disable=unused-variable, redefined-outer-name
def procedure_location(procedure_name: str) -> Union[Path, None]:
    """Take the name of a Procedure, find the corresponding file, and return its
    canonical location as a path, if it exists.
    Doesn't care if you include the extension."""

    name = procedure_name.rstrip(PROCEDURE_EXT)

    return next((path for path in state(iterator=True) if path.stem == name), None)


def friendly_prefix_for_path(path: Path):
    """Take a long path and return it with a friendly . or ~ where applicable"""

    path_string, home_string, cwd_string = map(str, [path.expanduser(), HOME, CWD])

    short_prefix, verbose_prefix = (
        (".", cwd_string) if cwd_string in path_string else ("~", home_string)
    )

    return path_string.replace(verbose_prefix, short_prefix)


def deserialize_procedure_file(procedure_path: Path) -> Procedure:
    """Take the content of a Procedure file, try to find the corresponding file,
    return it as a Procedure object"""

    fields: Dict = yml.load(procedure_path)

    return Procedure(path=procedure_path, **fields)


# no need to test stdlib
def procedure_file_metadata(file_location: Path) -> Dict:  # pragma: no cover
    """ A dict of:
        full_path
        last_modified
        last_accessed"""

    last_modified = ctime(getmtime(file_location))
    last_accessed = ctime(getatime(file_location))

    return {
        "last_modified": last_modified,
        "last_accessed": last_accessed,
        "full_path": file_location.resolve(),
    }


def procedure_object_metadata(procedure: Procedure) -> Dict:
    """A dict of:
        title
        description
        step_count
        context_vars
        knowns"""

    return {
        "title": procedure.title,
        # move the dashes into theatrics and just return falsy values here
        "description": procedure.description,
        "step_count": len(procedure.steps),
        "context_vars": [context_var_name(c) for c in procedure.context],
        "knowns": list(procedure.knowns),
    }


def path_to_write_to(global_: bool = False) -> Path:
    """Returns the path that a new Procedure file ought to be written to based on the
    presence of a .nothing directory in home cwd.

    SIDE EFFECT: Will create ~/.nothing if it does not exist
    and there is no ./.nothing.

    The idea is, you're not prioritizing local Procedures until you've called `not init`
    on your current directory."""

    if global_ or not CWD_DOT_NOTHING_DIR.exists():
        HOME_DOT_NOTHING_DIR.mkdir(exist_ok=True)
        return HOME_DOT_NOTHING_DIR

    return CWD_DOT_NOTHING_DIR


def collect_fancy_list_input() -> Dict[str, List[str]]:
    """Utility for show_fancy_list().

    Returns a dict with a key each for cwd and home (if they exist).
    The values are lists of Procedure names."""

    collection = defaultdict(list)
    for path in state(iterator=True):
        key = "global" if path.parent == HOME_DOT_NOTHING_DIR else "local"
        collection[key] += [path.stem]

    return collection
