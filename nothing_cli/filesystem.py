"""filesystem utilities for not"""
from itertools import chain
from os.path import getatime, getmtime
from pathlib import Path
from time import ctime
from typing import Dict, Iterable, Iterator, List, Union

from ruamel.yaml import YAML

from .constants import (
    CWD,
    CWD_DOT_NOTHING_DIR,
    DirectoryChoicesForListCommand,
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


# XXX i knew there was a glob for this:
# "*.y[?am]*l" would work accurately except in extremely bizarre edge cases
# such as like-- file.yamamaml or file.ymasdfsdl
# if you've done that to your .nothing dir, you deserve an error imo.
# would allow deprecation of this method in favor of [path].rglob("*.y[?am]*l")
# which might be nicer enough to warrant the drop in precision?
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

    path_string, home_string, cwd_string = map(str, [path.expanduser(), HOME, CWD])

    short_prefix, verbose_prefix = (
        (".", cwd_string) if cwd_string in path_string else ("~", home_string)
    )

    return path_string.replace(verbose_prefix, short_prefix)


def procedure_names_by_parent_dir_name(paths: Iterable[Path]) -> Dict[str, List[str]]:
    """Helper for collect_fancy_list_input.
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


# XXX would be better if this only took paths, since strings are really
# only passed during tests
def deserialize_procedure_file(procedure: Union[str, Path]) -> Procedure:
    """Take the content of a Procedure file, try to find the corresponding file,
    return it as a Procedure object"""

    yml: Dict = yaml.load(procedure)

    raw_steps = yml.pop("steps")
    raw_context = yml.pop("context", None)

    parsed_steps: List[Step] = steps_from_yaml_block(raw_steps)
    parsed_context: List[ContextItem] = context_items_from_yaml_list(raw_context)

    return Procedure(
        filename=getattr(procedure, "name", ""),
        steps=parsed_steps,
        context=parsed_context,
        **yml,
    )


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


def collect_fancy_list_input(
    showing_from_dir: DirectoryChoicesForListCommand,
) -> Dict[str, Dict[str, str]]:
    """Utility for show_fancy_list().

    Returns a dict with a key each for cwd and home.
    The values are dicts where the keys are human-friendly paths
    and the values are lists of Procedure names."""

    show_both: bool = showing_from_dir is DirectoryChoicesForListCommand.both
    show_home: bool = showing_from_dir is DirectoryChoicesForListCommand.home
    show_cwd: bool = showing_from_dir is DirectoryChoicesForListCommand.cwd

    names_by_dir = {}

    if show_home or show_both:
        procedures_in_home_dot_nothing_dir: Iterator[Path] = glob_each_extension(
            "*", HOME_DOT_NOTHING_DIR, recurse=True
        )

        names_by_dir["home"] = procedure_names_by_parent_dir_name(
            procedures_in_home_dot_nothing_dir
        )

    if show_cwd or show_both:
        procedures_in_cwd_dot_nothing_dir: Iterator[Path] = glob_each_extension(
            "*", CWD_DOT_NOTHING_DIR, recurse=True
        )

        names_by_dir["cwd"] = procedure_names_by_parent_dir_name(
            procedures_in_cwd_dot_nothing_dir
        )

    return names_by_dir
