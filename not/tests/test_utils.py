# pylint: disable=missing-function-docstring, redefined-outer-name

"""Tests for not.utils"""
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from .. import utils
from ..constants import VALID_TASK_SPEC_EXTENSION_NAMES, DOT_NOTHING_DIRECTORY_NAME

SAMPLE_TASK_SPEC_NAMES = [
    "code_review_checklist",
    "release_hounds",
    "dazzle_friends",
]


@pytest.fixture(scope="module")
def dot_not_dir_with_a_file_of_each_extension() -> Path:
    """The path to a directory containing 3 Task Spec files,
    one with each of the valid extensions."""

    with TemporaryDirectory() as tempdir:
        for name, extension in zip(
            SAMPLE_TASK_SPEC_NAMES, VALID_TASK_SPEC_EXTENSION_NAMES
        ):
            dot_nothing_directory = Path(tempdir) / DOT_NOTHING_DIRECTORY_NAME
            dot_nothing_directory.mkdir(exist_ok=True)

            task_spec = dot_nothing_directory / f"{name}.{extension}"
            task_spec.touch(exist_ok=True)

        yield tempdir


def test_task_spec_location_finds_any_extension_under_home_dot_nothing_dir(
    dot_not_dir_with_a_file_of_each_extension, monkeypatch
):
    def mock_dir():
        return Path(dot_not_dir_with_a_file_of_each_extension)

    monkeypatch.setattr(Path, "home", mock_dir)

    for name in SAMPLE_TASK_SPEC_NAMES:
        location: Path = utils.task_spec_location(name)
        assert name in location.name


def test_task_spec_location_finds_any_extension_under_local_dot_nothing_dir(
    dot_not_dir_with_a_file_of_each_extension, monkeypatch
):
    def mock_dir():
        return Path(dot_not_dir_with_a_file_of_each_extension)

    monkeypatch.setattr(Path, "cwd", mock_dir)

    location = utils.task_spec_location(SAMPLE_TASK_SPEC_NAMES[0])
    assert location is not None
    assert SAMPLE_TASK_SPEC_NAMES[0] in location.name


@pytest.fixture(scope="module")
def ancestor_of_this_dir_has_dot_nothing_dir() -> Path:
    with TemporaryDirectory() as tempdir:
        dot_nothing_directory = Path(tempdir) / DOT_NOTHING_DIRECTORY_NAME
        dot_nothing_directory.mkdir(exist_ok=True)

        working_directory = Path(tempdir) / "child_dir"
        working_directory.mkdir(exist_ok=True)

        yield working_directory


def test_task_spec_location_does_not_find_spec_in_ancestor_dot_nothing_dir(
    ancestor_of_this_dir_has_dot_nothing_dir, monkeypatch
):
    def mock_dir():
        return Path(ancestor_of_this_dir_has_dot_nothing_dir)

    monkeypatch.setattr(Path, "cwd", mock_dir)

    location = utils.task_spec_location(SAMPLE_TASK_SPEC_NAMES[0])
    assert location is None


@pytest.fixture
def dir_containing_dot_not_file():
    with TemporaryDirectory() as tempdir:
        task_spec_name = "speed-reading"
        filename = f"{task_spec_name}.not"
        task_spec = Path(tempdir) / filename
        task_spec.touch(exist_ok=True)

        yield tempdir, task_spec_name


def test_task_spec_location_finds_local_dot_not_file(
    dir_containing_dot_not_file, monkeypatch
):
    directory, spec_name = dir_containing_dot_not_file

    def mock_dir():
        return Path(directory)

    monkeypatch.setattr(Path, "cwd", mock_dir)

    location = utils.task_spec_location(spec_name)
    assert location is not None
    assert spec_name in location.name


@pytest.fixture
def ancestor_of_this_dir_has_dot_not_file():
    with TemporaryDirectory() as tempdir:
        filename = "cooking-soup.not"
        task_spec = Path(tempdir) / filename
        task_spec.touch(exist_ok=True)

        working_directory = Path(tempdir) / "child_dir"
        working_directory.mkdir(exist_ok=True)

        yield working_directory


def test_task_spec_location_does_not_find_dot_not_file_in_ancestor_dir(
    ancestor_of_this_dir_has_dot_not_file, monkeypatch
):
    def mock_dir():
        return Path(ancestor_of_this_dir_has_dot_not_file)

    monkeypatch.setattr(Path, "cwd", mock_dir)
    location = utils.task_spec_location(SAMPLE_TASK_SPEC_NAMES[0])
    assert location is None
