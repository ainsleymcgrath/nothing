from itertools import chain
from pathlib import Path
from typing import Iterator, Union

from .constants import NOTHINGFILE_EXTENSION_NAMES, NOTHINGFILE_DIRECTORY_NAME


def nothingfile_location(nothingfile_name: str) -> Union[Path, None]:
    """Take the name of a Nothingfile and try to return its canonical location as a path"""

    dot_nothings_directories_below_cwd = Path.cwd().glob(NOTHINGFILE_DIRECTORY_NAME)
    dot_nothings_directories_below_home = Path.home().glob(NOTHINGFILE_DIRECTORY_NAME)

    def _glob_each_extension(path: Path):
        for ext in NOTHINGFILE_EXTENSION_NAMES:
            yield from path.glob(f"**/{nothingfile_name}.{ext}")

    valid_task_specs_in_dot_nothings_directories: Iterator[Iterator] = (
        _glob_each_extension(path)
        for path in chain(
            dot_nothings_directories_below_cwd, dot_nothings_directories_below_home
        )
    )

    dot_not_files_below_cwd = Path.cwd().glob("**/{nothingfile_name}.not")

    any_place_a_task_spec_can_be = chain(
        dot_not_files_below_cwd, *valid_task_specs_in_dot_nothings_directories
    )

    return next(any_place_a_task_spec_can_be, None)
