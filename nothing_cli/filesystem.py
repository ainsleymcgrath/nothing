"""filesystem utilities for not"""
from itertools import chain
from os.path import getatime, getmtime
from pathlib import Path
from time import ctime
from typing import Dict, Iterable, Iterator, List, Union
from typing_extensions import Literal

from ruamel.yaml import YAML

from .constants import (
    CWD,
    CWD_DOT_NOTHING_DIR,
    HOME,
    HOME_DOT_NOTHING_DIR,
    PROCEDURE_EXT_PATTERN,
    VALID_PROCEDURE_EXTENSION_NAMES,
)
from .localization import polyglot as glot
from .models import (
    ContextItem,
    context_items_from_yaml_list,
    Step,
    steps_from_yaml_block,
    Procedure,
)

yaml = YAML()


def glob_each_extension(
    procedure_name_glob: str, path: Path, recurse=False
) -> Iterator[Path]:
    """For each extention in not.constants.VALID_PROCEDURE_EXTENSION_NAMES,
    glob for the provided procedure_name"""

    for ext in VALID_PROCEDURE_EXTENSION_NAMES:
        glob_str = (
            f"**/{procedure_name_glob}.{ext}"
            if recurse
            else f"{procedure_name_glob}.{ext}"
        )
        yield from path.glob(glob_str)


def procedure_location(procedure_name: str) -> Union[Path, None]:
    """Take the name of a Procedure, find the corresponding file, and return its
    canonical location as a path, if it exists"""

    procedures_in_home_dot_nothing_dir: Iterator[Path] = glob_each_extension(
        procedure_name, HOME_DOT_NOTHING_DIR, recurse=True
    )

    procedures_below_cwd_dot_nothing_dir: Iterator[Path] = glob_each_extension(
        procedure_name, CWD_DOT_NOTHING_DIR, recurse=True
    )

    any_place_the_procedure_could_be = chain(
        procedures_below_cwd_dot_nothing_dir, procedures_in_home_dot_nothing_dir
    )

    return next(any_place_the_procedure_could_be, None)


def friendly_prefix_for_path(path: Path):
    """Take a long path and return it with a friendly . or ~ where applicable"""

    path_string, home_string, cwd_string = map(str, [path, HOME, CWD])

    short_prefix, verbose_prefix = (
        (".", cwd_string) if cwd_string in path_string else ("~", home_string)
    )

    return path_string.replace(verbose_prefix, short_prefix)


def procedure_names_by_parent_dir_name(
    paths: Iterable[Path], base_dir: Literal["home", "cwd"] = None
) -> Dict[str, List[str]]:
    """Helper for theatrics._collect_fancy_list_input.
    Returns a dict with friendly path name keys and lists of friendly Procedure
    names as values."""

    accum_dict = {}

    for path in paths:
        if not path.is_file():
            continue

        key = friendly_prefix_for_path(path.parent)
        if key in accum_dict:
            accum_dict[key] += [PROCEDURE_EXT_PATTERN.sub("", path.name)]
            continue

        accum_dict[key] = [PROCEDURE_EXT_PATTERN.sub("", path.name)]

    return accum_dict


def deserialize_procedure_file(procedure_content: str) -> Procedure:
    """Take the content of a Procedure file, try to find the corresponding file,
    return it as a Procedure object"""

    yml: Dict = yaml.load(procedure_content)

    raw_steps = yml.pop("steps")
    raw_context = yml.pop("context", None)

    parsed_steps: List[Step] = steps_from_yaml_block(raw_steps)
    parsed_context: List[ContextItem] = context_items_from_yaml_list(raw_context)

    return Procedure(steps=parsed_steps, context=parsed_context, **yml)


def procedure_file_metadata(file_location: Path) -> Dict:
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
        step_count
        context_vars"""

    return {
        "title": procedure.title,
        "description": procedure.description,
        "step_count": len(procedure.steps),
        "context_vars": [c.var_name for c in procedure.context]
        if procedure.context
        else glot["no_context_to_display_placeholder"],
    }


def path_to_write_to(global_: bool) -> Path:
    """Returns the path that a new Procedure file ought to be written to based on the
    presence of a .nothing directory in home cwd.

    SIDE EFFECT: Will create ~/.nothing if it does not exist
    and there is no ./.nothing"""

    if global_ or not CWD_DOT_NOTHING_DIR.exists():
        HOME_DOT_NOTHING_DIR.mkdir(exist_ok=True)
        return HOME_DOT_NOTHING_DIR

    return CWD_DOT_NOTHING_DIR
