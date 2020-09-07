# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""test suite for filesystem.path_to_write_to"""

from pathlib import Path

import pytest

from ...filesystem import path_to_write_to


def test_cwd_dot_nothing_exists(existing_cwd_dot_nothing_dir: Path):
    assert path_to_write_to() == existing_cwd_dot_nothing_dir
    assert (
        path_to_write_to(global_=True) != existing_cwd_dot_nothing_dir
    ), "~/.nothing is created if it doesn't exist"


@pytest.fixture
def only_home_dot_nothing_dir_exists(
    existing_home_dot_nothing_dir: Path, existing_cwd_dot_nothing_dir: Path
) -> Path:
    existing_cwd_dot_nothing_dir.rmdir()

    return existing_home_dot_nothing_dir


def test_only_home_dot_nothing_dir_exists(only_home_dot_nothing_dir_exists: Path):
    assert (
        path_to_write_to(global_=True)
        == only_home_dot_nothing_dir_exists
        == path_to_write_to()
    )


def test_both_dot_nothing_dirs_exist(
    existing_cwd_dot_nothing_dir: Path, existing_home_dot_nothing_dir: Path
):
    assert path_to_write_to() == existing_cwd_dot_nothing_dir

    assert path_to_write_to(global_=True) == existing_home_dot_nothing_dir
