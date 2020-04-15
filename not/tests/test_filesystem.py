# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument
# pylint: disable=no-self-use

"""Tests for not.utils"""
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from ..constants import VALID_TASK_SPEC_EXTENSION_NAMES, DOT_NOTHING_DIRECTORY_NAME
from ..filesystem import glob_each_extension, task_spec_location

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


class TestTaskSpecLocation:
    """Test suite for not.filesytem.task_spec_location"""

    def test_task_spec_location_finds_any_extension_under_home_dot_nothing_dir(
        self, dot_not_dir_with_a_file_of_each_extension, monkeypatch
    ):
        def mock_dir():
            return Path(dot_not_dir_with_a_file_of_each_extension)

        monkeypatch.setattr(Path, "home", mock_dir)

        for name in SAMPLE_TASK_SPEC_NAMES:
            location: Path = task_spec_location(name)
            assert name in location.name

    def test_task_spec_location_finds_any_extension_under_local_dot_nothing_dir(
        self, dot_not_dir_with_a_file_of_each_extension, monkeypatch
    ):
        def mock_dir():
            return Path(dot_not_dir_with_a_file_of_each_extension)

        monkeypatch.setattr(Path, "cwd", mock_dir)

        location = task_spec_location(SAMPLE_TASK_SPEC_NAMES[0])
        assert location is not None
        assert SAMPLE_TASK_SPEC_NAMES[0] in location.name

    @pytest.fixture(scope="module")
    def ancestor_of_this_dir_has_dot_nothing_dir(self) -> Path:
        with TemporaryDirectory() as tempdir:
            dot_nothing_directory = Path(tempdir) / DOT_NOTHING_DIRECTORY_NAME
            dot_nothing_directory.mkdir(exist_ok=True)

            working_directory = Path(tempdir) / "child_dir"
            working_directory.mkdir(exist_ok=True)

            yield working_directory

    def test_task_spec_location_does_not_find_spec_in_ancestor_dot_nothing_dir(
        self, ancestor_of_this_dir_has_dot_nothing_dir, monkeypatch
    ):
        def mock_dir():
            return Path(ancestor_of_this_dir_has_dot_nothing_dir)

        monkeypatch.setattr(Path, "cwd", mock_dir)

        location = task_spec_location(SAMPLE_TASK_SPEC_NAMES[0])
        assert location is None

    @pytest.fixture
    def dir_containing_dot_not_file(self):
        with TemporaryDirectory() as tempdir:
            task_spec_name = "speed-reading"
            filename = f"{task_spec_name}.not"
            task_spec = Path(tempdir) / filename
            task_spec.touch(exist_ok=True)

            yield tempdir, task_spec_name

    def test_task_spec_location_finds_local_dot_not_file(
        self, dir_containing_dot_not_file, monkeypatch
    ):
        directory, spec_name = dir_containing_dot_not_file

        def mock_dir():
            return Path(directory)

        monkeypatch.setattr(Path, "cwd", mock_dir)

        location = task_spec_location(spec_name)
        assert location is not None
        assert spec_name in location.name

    @pytest.fixture
    def ancestor_of_this_dir_has_dot_not_file(self):
        with TemporaryDirectory() as tempdir:
            filename = "cooking-soup.not"
            task_spec = Path(tempdir) / filename
            task_spec.touch(exist_ok=True)

            working_directory = Path(tempdir) / "child_dir"
            working_directory.mkdir(exist_ok=True)

            yield working_directory

    def test_task_spec_location_does_not_find_dot_not_file_in_ancestor_dir(
        self, ancestor_of_this_dir_has_dot_not_file, monkeypatch
    ):
        def mock_dir():
            return Path(ancestor_of_this_dir_has_dot_not_file)

        monkeypatch.setattr(Path, "cwd", mock_dir)
        location = task_spec_location(SAMPLE_TASK_SPEC_NAMES[0])
        assert location is None


class TestGlobEachExtension:
    """Test suite for not.filesystem.glob_each_extension"""

    HTML_FILE = "bar.html"
    PYTHON_FILE = "foo.py"
    NESTED_DIRECTORY = "buzz"
    SUPERFLUOUS_FILE_UNDER_NESTED_DIR = "fizz.clj"
    RELEVANT_FILE_UNDER_NESTED_DIR = "foobar.not"

    @pytest.fixture(scope="class")
    def dir_with_a_file_of_each_extension_and_superfluous_files(
        self, dot_not_dir_with_a_file_of_each_extension
    ):
        # repurposing the dot nothing dir since it has valid specs in it
        dir_to_yield = (
            Path(dot_not_dir_with_a_file_of_each_extension) / DOT_NOTHING_DIRECTORY_NAME
        )
        python_file = dir_to_yield / self.PYTHON_FILE
        html_file = dir_to_yield / self.HTML_FILE

        python_file.touch(exist_ok=True)
        html_file.touch(exist_ok=True)

        nested_directory = dir_to_yield / self.NESTED_DIRECTORY
        file_under_nested_directory = (
            nested_directory / self.SUPERFLUOUS_FILE_UNDER_NESTED_DIR
        )
        task_spec_under_nested_directory = (
            nested_directory / self.RELEVANT_FILE_UNDER_NESTED_DIR
        )

        nested_directory.mkdir(exist_ok=True)
        file_under_nested_directory.touch(exist_ok=True)
        task_spec_under_nested_directory.touch(exist_ok=True)

        yield dir_to_yield

    def test_without_recurse(
        self, dir_with_a_file_of_each_extension_and_superfluous_files
    ):
        task_spec_files_in_dir = glob_each_extension(
            "*", dir_with_a_file_of_each_extension_and_superfluous_files
        )

        names_of_returned_files = (
            path.name.split(".")[-2] for path in task_spec_files_in_dir
        )
        assert set(names_of_returned_files) == set(SAMPLE_TASK_SPEC_NAMES)
        assert self.SUPERFLUOUS_FILE_UNDER_NESTED_DIR not in task_spec_files_in_dir

    def test_with_recurse(
        self, dir_with_a_file_of_each_extension_and_superfluous_files
    ):
        task_spec_files_in_dir = glob_each_extension(
            "*", dir_with_a_file_of_each_extension_and_superfluous_files, recurse=True
        )

        names_of_returned_files = set(
            path.name.split(".")[-2] for path in task_spec_files_in_dir
        )
        expected_names = {
            self.RELEVANT_FILE_UNDER_NESTED_DIR.split(".")[-2],
            *SAMPLE_TASK_SPEC_NAMES,
        }

        assert names_of_returned_files == expected_names


class TestCWDTaskSpecs:
    """Test suite for not.filesystem.cwd_task_specs"""


class TestHomeDotNothingDirTaskSpecs:
    """Test suite for not.filesystem.home_dot_nothing_dir_task_specs"""
