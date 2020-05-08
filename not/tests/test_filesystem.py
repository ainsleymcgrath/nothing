# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument
# pylint: disable=no-self-use

"""Tests for not.utils"""
from pathlib import Path
from typing import Iterator

import pytest

from ..constants import VALID_TASK_SPEC_EXTENSION_NAMES, DOT_NOTHING_DIRECTORY_NAME
from ..filesystem import glob_each_extension, task_spec_location

SAMPLE_TASK_SPEC_NAMES = [
    "code_review_checklist",
    "release_hounds",
    "dazzle_friends",
]


@pytest.fixture
def dir_with_each_file_type_in_dot_nothing_subdir(tmp_path) -> Path:
    """The path to a directory containing 3 Task Spec files,
    one with each of the valid extensions."""

    for name, extension in zip(SAMPLE_TASK_SPEC_NAMES, VALID_TASK_SPEC_EXTENSION_NAMES):
        dot_nothing_directory = Path(tmp_path) / DOT_NOTHING_DIRECTORY_NAME
        dot_nothing_directory.mkdir(exist_ok=True)

        task_spec = dot_nothing_directory / f"{name}.{extension}"
        task_spec.touch(exist_ok=True)

    return tmp_path


@pytest.fixture
def patched_cwd(dir_with_each_file_type_in_dot_nothing_subdir, monkeypatch) -> None:
    def mock_dir():
        return Path(dir_with_each_file_type_in_dot_nothing_subdir)

    monkeypatch.setattr(Path, "cwd", mock_dir)
    return dir_with_each_file_type_in_dot_nothing_subdir


@pytest.fixture
def patched_home(dir_with_each_file_type_in_dot_nothing_subdir, monkeypatch) -> None:
    def mock_dir():
        return Path(dir_with_each_file_type_in_dot_nothing_subdir)

    monkeypatch.setattr(Path, "home", mock_dir)
    return dir_with_each_file_type_in_dot_nothing_subdir


class TestTaskSpecLocation:
    """Test suite for not.filesytem.task_spec_location"""

    @pytest.mark.parametrize("name", SAMPLE_TASK_SPEC_NAMES)
    def test_under_home_dot_nothing_dir(self, name, patched_home):
        location: Path = task_spec_location(name)

        assert name in location.name
        assert patched_home.name in str(location)

    @pytest.mark.parametrize("name", SAMPLE_TASK_SPEC_NAMES)
    def test_local_dot_nothing_dir(self, name, patched_cwd):
        location = task_spec_location(name)

        assert name in location.name
        assert patched_cwd.name in str(location)

    @pytest.fixture
    def parent_of_this_dir_has_dot_nothing_dir(self, tmp_path) -> Path:
        dot_nothing_directory = tmp_path / DOT_NOTHING_DIRECTORY_NAME
        dot_nothing_directory.mkdir(exist_ok=True)

        working_directory = tmp_path / "child_dir"
        working_directory.mkdir(exist_ok=True)

        return working_directory

    @pytest.mark.parametrize("name", SAMPLE_TASK_SPEC_NAMES)
    def test_location_does_not_find_spec_in_parent_dot_nothing_dir(self, name):
        location = task_spec_location(name)

        assert location is None

    @pytest.fixture
    def task_spec_with_dot_not_extension(self, tmp_path):
        task_spec_name = "speed-reading"
        filename = f"{task_spec_name}.not"
        task_spec = Path(tmp_path) / filename
        task_spec.touch(exist_ok=True)

        return task_spec_name

    def test_task_spec_location_finds_local_dot_not_file(
        self, task_spec_with_dot_not_extension, patched_cwd
    ):
        spec_name = task_spec_with_dot_not_extension
        location = task_spec_location(spec_name)

        assert spec_name in location.name

    @pytest.fixture
    def dot_not_file_in_parent_dir(self, tmp_path):
        filename = "cooking-soup.not"
        task_spec = Path(tmp_path) / filename
        task_spec.touch(exist_ok=True)

        working_directory = Path(tmp_path) / "child_dir"
        working_directory.mkdir(exist_ok=True)

        return working_directory

    def test_does_not_find_dot_not_file_in_parent_dir(self, dot_not_file_in_parent_dir):
        location = task_spec_location("cooking-soup")
        assert location is None


class TestGlobEachExtension:
    """Test suite for not.filesystem.glob_each_extension"""

    HTML_FILE = "bar.html"
    PYTHON_FILE = "foo.py"
    SUBDIR = "nested_dir"
    CLJ_FILE_IN_SUBDIR = "fizz.clj"
    DOT_NOT_FILE_IN_SUBDIR = "foobar.not"

    @pytest.fixture
    def dir_with_task_specs_and_other_files_and_subdir(self, tmp_path):
        python_file = tmp_path / self.PYTHON_FILE
        html_file = tmp_path / self.HTML_FILE
        task_spec_files: Iterator[Path] = (
            tmp_path / f"{name}.{ext}"
            for name, ext in zip(
                SAMPLE_TASK_SPEC_NAMES, VALID_TASK_SPEC_EXTENSION_NAMES
            )
        )

        nested_directory = tmp_path / self.SUBDIR
        nested_directory.mkdir(exist_ok=True)

        file_under_nested_directory = nested_directory / self.CLJ_FILE_IN_SUBDIR
        task_spec_in_subdir = nested_directory / self.DOT_NOT_FILE_IN_SUBDIR

        for file in [
            python_file,
            html_file,
            file_under_nested_directory,
            task_spec_in_subdir,
            *task_spec_files,
        ]:
            file.touch(exist_ok=True)

        return tmp_path

    def test_without_recurse(self, dir_with_task_specs_and_other_files_and_subdir):
        task_spec_files_in_dir = glob_each_extension(
            "*", dir_with_task_specs_and_other_files_and_subdir
        )

        names_of_returned_files = (
            path.name.split(".")[-2] for path in task_spec_files_in_dir
        )

        assert set(names_of_returned_files) == set(SAMPLE_TASK_SPEC_NAMES)
        assert self.CLJ_FILE_IN_SUBDIR not in task_spec_files_in_dir

    def test_with_recurse(self, dir_with_task_specs_and_other_files_and_subdir):
        task_spec_files_in_dir = glob_each_extension(
            "*", dir_with_task_specs_and_other_files_and_subdir, recurse=True
        )

        names_of_returned_files = set(
            path.name.split(".")[-2] for path in task_spec_files_in_dir
        )
        expected_names: set = {
            self.DOT_NOT_FILE_IN_SUBDIR.split(".")[-2],
            *SAMPLE_TASK_SPEC_NAMES,
        }

        assert names_of_returned_files == expected_names
