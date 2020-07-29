# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test suite for not.theatrics._friendly_prefix_for_path"""
import pytest

from ...filesystem import friendly_prefix_for_path


@pytest.fixture
def file_in_home(patched_filesystem):
    home, _ = patched_filesystem
    file = home / "poems.txt"
    file.touch()

    return file


@pytest.fixture
def file_in_cwd(patched_filesystem):
    _, cwd = patched_filesystem
    file = cwd / "stories.txt"
    file.touch()

    return file


@pytest.fixture
def file_in_grandchild_of_home(patched_filesystem):
    home, _ = patched_filesystem
    grandchild_dir = home / "child" / "grandchild"
    file = grandchild_dir / "recipes.txt"

    grandchild_dir.mkdir(parents=True)
    file.touch()

    return file


def test_home_prefix(file_in_home):
    assert friendly_prefix_for_path(file_in_home) == "~/poems.txt"


def test_cwd_prefix(file_in_cwd):
    assert friendly_prefix_for_path(file_in_cwd) == "./stories.txt"


def test_ancestor_prefix(file_in_grandchild_of_home):
    assert (
        friendly_prefix_for_path(file_in_grandchild_of_home)
        == "~/child/grandchild/recipes.txt"
    )
