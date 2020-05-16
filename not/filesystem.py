"""filesystem utilities for not"""
from itertools import chain
from pathlib import Path
from typing import Iterator, Union

from .constants import (
    DOT_NOTHING_DIRECTORY_NAME,
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
