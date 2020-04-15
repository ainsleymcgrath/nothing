"""filesystem utilities for not"""
from itertools import chain
from pathlib import Path
from typing import Dict, Iterator, Literal, List, Union

from .constants import (
    DOT_NOTHING_DIRECTORY_NAME,
    VALID_TASK_SPEC_EXTENSION_NAMES,
)
from .models import TaskSpec


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

    task_specs_in_home_dot_nothing_dir: Iterator[Iterator] = (
        glob_each_extension(task_spec_name, path) for path in home_dot_nothing_dir
    )

    task_specs_below_cwd_dot_nothing_dir: Iterator[Iterator] = (
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


def cwd_task_spec_file_names_by_location() -> Dict[
    Literal["cwd_dot_nothing_dir", "cwd_dot_not_files"], List[TaskSpec]
]:
    """Return TaskSpec objects for each task spec file
    in [cwd]/.nothing and/or any [cwd]/*.not files."""

    cwd_dot_nothing_dir = next(Path.cwd().glob(DOT_NOTHING_DIRECTORY_NAME), None)

    cwd_task_spec_names: List = (
        [  # preserve task spec file names wih literal . in them
            ".".join(path.name).split(".")
            for path in glob_each_extension("*", cwd_dot_nothing_dir)
        ]
        if cwd_dot_nothing_dir is not None
        else []
    )

    cwd_dot_not_file_names: List = [
        ".".join(path.name).split(".") for path in Path.cwd().glob(f"**/*.not")
    ]

    return {
        "cwd_dot_nothing_dir": cwd_task_spec_names,
        "cwd_dot_not_files": cwd_dot_not_file_names,
    }


def home_dot_nothing_dir_task_spec_names() -> Dict[
    Literal["home_dot_nothing_dir"], List[TaskSpec]
]:
    """Return TaskSpec objects for each task spec file under ~/.nothing."""
    home_dot_nothing_dir = Path.home() / DOT_NOTHING_DIRECTORY_NAME

    home_dot_nothing_dir_task_spec_file_names: List = [
        ".".join(path.name).split(".")
        for path in glob_each_extension("*", home_dot_nothing_dir)
    ]

    return {"home_dot_nothing_dir": home_dot_nothing_dir_task_spec_file_names}
