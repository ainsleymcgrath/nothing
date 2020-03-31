from itertools import chain
from pathlib import Path
from typing import Iterator, Union

from .constants import VALID_TASK_SPEC_EXTENSION_NAMES, DOT_NOTHING_DIRECTORY_NAME


def task_spec_location(spec_name: str) -> Union[Path, None]:
    """Take the name of a Task Spec file and try to return its canonical location as a path"""

    cwd_dot_nothing_dir, home_dot_nothing_dir = (
        path.glob(DOT_NOTHING_DIRECTORY_NAME) for path in [Path.cwd(), Path.home()]
    )

    def _glob_each_extension(path: Path, recurse=False):
        for ext in VALID_TASK_SPEC_EXTENSION_NAMES:
            glob_str = f"**/{spec_name}.{ext}" if recurse else f"{spec_name}.{ext}"
            yield from path.glob(glob_str)

    task_specs_in_home_dot_nothing_dir: Iterator[Iterator] = (
        _glob_each_extension(path) for path in home_dot_nothing_dir
    )

    task_specs_below_cwd_dot_nothing_dir: Iterator[Iterator] = (
        _glob_each_extension(path, recurse=True) for path in cwd_dot_nothing_dir
    )

    dot_not_files_below_cwd = Path.cwd().glob(f"**/{spec_name}.not")

    any_place_a_task_spec_can_be = chain(
        dot_not_files_below_cwd,
        *task_specs_below_cwd_dot_nothing_dir,
        *task_specs_in_home_dot_nothing_dir,
    )

    return next(any_place_a_task_spec_can_be, None)
