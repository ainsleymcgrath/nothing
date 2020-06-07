"""filesystem utilities for not"""
from itertools import chain
from pathlib import Path
from typing_extensions import Literal
from typing import Dict, Iterable, Iterator, List, Union

from .constants import (
    DOT_NOTHING_DIRECTORY_NAME,
    TASK_SPEC_EXT_PATTERN,
    VALID_TASK_SPEC_EXTENSION_NAMES,
)


def glob_each_extension(
    task_spec_name_glob: str, path: Path, recurse=False
) -> Iterator[Path]:
    """For each extention in not.constants.VALID_TASK_SPEC_EXTENSION_NAMES,
    glob for the provided task_spec_name"""

    for ext in VALID_TASK_SPEC_EXTENSION_NAMES:
        glob_str = (
            f"**/{task_spec_name_glob}.{ext}"
            if recurse
            else f"{task_spec_name_glob}.{ext}"
        )
        yield from path.glob(glob_str)


def task_spec_location(task_spec_name: str) -> Union[Path, None]:
    """Take the name of a Task Spec, find the corresponding file, and return its
    canonical location as a path, if it exists"""

    cwd_dot_nothing_dir, home_dot_nothing_dir = (
        path.glob(DOT_NOTHING_DIRECTORY_NAME) for path in [Path.cwd(), Path.home()]
    )

    task_specs_in_home_dot_nothing_dir: Iterator[Path] = chain(
        glob_each_extension(task_spec_name, path) for path in home_dot_nothing_dir
    )

    task_specs_below_cwd_dot_nothing_dir: Iterator[Path] = chain(
        glob_each_extension(task_spec_name, path, recurse=True)
        for path in cwd_dot_nothing_dir
    )

    dot_not_files_below_cwd = Path.cwd().glob(f"**/{task_spec_name}.not")

    any_place_the_task_spec_could_be = chain(
        dot_not_files_below_cwd,
        *task_specs_below_cwd_dot_nothing_dir,
        *task_specs_in_home_dot_nothing_dir,
    )

    return next(any_place_the_task_spec_could_be, None)


def friendly_prefix_for_path(path: Path, location: Literal["home", "cwd"]):
    """Take a long path and return it with a friendly . or ~ where applicable"""

    # TODO ditch the location kwarg, do check if path is child of cwd?
    prefixes_by_location = {"home": "~", "cwd": "."}
    verbose_prefix = str(getattr(Path, location)())

    return str(path).replace(verbose_prefix, prefixes_by_location[location])


def task_spec_names_by_parent_dir_name(
    paths: Iterable[Path], base_dir: Literal["home", "cwd"] = None
) -> Dict[str, List[str]]:
    """Helper for _collect_fancy_list_input.
    Returns a dict with friendly path name keys and lists of friendly task spec
    names as values."""

    accum_dict = {}

    for path in paths:
        if not path.is_file():
            continue

        key = friendly_prefix_for_path(path.parent, base_dir)
        if key in accum_dict:
            accum_dict[key] += [TASK_SPEC_EXT_PATTERN.sub("", path.name)]
            continue

        accum_dict[key] = [TASK_SPEC_EXT_PATTERN.sub("", path.name)]

    return accum_dict
