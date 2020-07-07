# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument
# pylint: disable=no-self-use

"""Tests for not.filesystem"""
from pathlib import Path
from typing import Iterator

import pytest

from .. import filesystem
from ..constants import (
    DirectoryChoicesForListCommand,
    VALID_PROCEDURE_EXTENSION_NAMES,
    DOT_NOTHING_DIRECTORY_NAME,
)
from ..filesystem import (
    collect_fancy_list_input,
    deserialize_procedure_file,
    friendly_prefix_for_path,
    glob_each_extension,
    procedure_location,
    procedure_object_metadata,
)
from ..localization import polyglot as glot


SAMPLE_PROCEDURE_NAMES = {"code_review_checklist", "release_hounds"}


@pytest.fixture
def dir_with_each_file_type_in_dot_nothing_subdir(tmp_path) -> Path:
    """The path to a directory containing 2 Procedure files,
    one with each of the valid extensions."""

    for name, extension in zip(SAMPLE_PROCEDURE_NAMES, VALID_PROCEDURE_EXTENSION_NAMES):
        dot_nothing_directory = Path(tmp_path) / DOT_NOTHING_DIRECTORY_NAME
        dot_nothing_directory.mkdir(exist_ok=True)

        procedure = dot_nothing_directory / f"{name}.{extension}"
        procedure.touch(exist_ok=True)

    return tmp_path


@pytest.fixture
def patched_cwd(dir_with_each_file_type_in_dot_nothing_subdir, monkeypatch) -> None:

    monkeypatch.setattr(
        filesystem, "CWD_DOT_NOTHING_DIR", dir_with_each_file_type_in_dot_nothing_subdir
    )
    return dir_with_each_file_type_in_dot_nothing_subdir


@pytest.fixture
def patched_home(dir_with_each_file_type_in_dot_nothing_subdir, monkeypatch) -> None:
    monkeypatch.setattr(
        filesystem,
        "HOME_DOT_NOTHING_DIR",
        dir_with_each_file_type_in_dot_nothing_subdir,
    )

    return dir_with_each_file_type_in_dot_nothing_subdir


class TestProcedureLocation:
    """Test suite for not.filesytem.procedure_location"""

    @pytest.mark.parametrize("name", SAMPLE_PROCEDURE_NAMES)
    def test_under_home_dot_nothing_dir(self, name, patched_home):
        location: Path = procedure_location(name)

        assert name in location.name
        assert patched_home.name in str(location)

    @pytest.mark.parametrize("name", SAMPLE_PROCEDURE_NAMES)
    def test_local_dot_nothing_dir(self, name, patched_cwd):
        location = procedure_location(name)

        assert name in location.name
        assert patched_cwd.name in str(location)

    @pytest.fixture
    def parent_of_this_dir_has_dot_nothing_dir(self, tmp_path) -> Path:
        dot_nothing_directory = tmp_path / DOT_NOTHING_DIRECTORY_NAME
        dot_nothing_directory.mkdir(exist_ok=True)

        working_directory = tmp_path / "child_dir"
        working_directory.mkdir(exist_ok=True)

        return working_directory

    @pytest.mark.parametrize("name", SAMPLE_PROCEDURE_NAMES)
    def test_location_does_not_find_spec_in_parent_dot_nothing_dir(self, name):
        location = procedure_location(name)

        assert location is None


class TestGlobEachExtension:
    """Test suite for not.filesystem.glob_each_extension"""

    HTML_FILE = "bar.html"
    PYTHON_FILE = "foo.py"
    SUBDIR = "nested_dir"
    CLJ_FILE_IN_SUBDIR = "fizz.clj"

    @pytest.fixture
    def dir_with_procedures_and_other_files_and_subdir(self, tmp_path):
        python_file = tmp_path / self.PYTHON_FILE
        html_file = tmp_path / self.HTML_FILE
        procedure_files: Iterator[Path] = (
            tmp_path / f"{name}.{ext}"
            for name, ext in zip(
                SAMPLE_PROCEDURE_NAMES, VALID_PROCEDURE_EXTENSION_NAMES
            )
        )

        nested_directory = tmp_path / self.SUBDIR
        nested_directory.mkdir(exist_ok=True)

        file_under_nested_directory = nested_directory / self.CLJ_FILE_IN_SUBDIR

        for file in [
            python_file,
            html_file,
            file_under_nested_directory,
            *procedure_files,
        ]:
            file.touch(exist_ok=True)

        return tmp_path

    def test_without_recurse(self, dir_with_procedures_and_other_files_and_subdir):
        procedure_files_in_dir = glob_each_extension(
            "*", dir_with_procedures_and_other_files_and_subdir
        )

        names_of_returned_files = (
            path.name.split(".")[-2] for path in procedure_files_in_dir
        )

        assert set(names_of_returned_files) == SAMPLE_PROCEDURE_NAMES
        assert self.CLJ_FILE_IN_SUBDIR not in procedure_files_in_dir

    def test_with_recurse(self, dir_with_procedures_and_other_files_and_subdir):
        procedure_files_in_dir = glob_each_extension(
            "*", dir_with_procedures_and_other_files_and_subdir, recurse=True
        )

        names_of_returned_files = set(
            path.name.split(".")[-2] for path in procedure_files_in_dir
        )

        assert names_of_returned_files == SAMPLE_PROCEDURE_NAMES


class TestFriendlyPrefixForPath:
    """Test suite for not.theatrics._friendly_prefix_for_path"""

    @pytest.fixture
    def file_in_home(self, tmp_path, monkeypatch):
        file = tmp_path / "poems.txt"
        file.touch(exist_ok=True)

        monkeypatch.setattr(filesystem, "HOME", tmp_path)

        return file

    @pytest.fixture
    def file_in_cwd(self, tmp_path, monkeypatch):
        cwd = tmp_path / "working_directory"
        cwd.mkdir(exist_ok=True)
        file = cwd / "stories.txt"
        file.touch(exist_ok=True)

        monkeypatch.setattr(filesystem, "CWD", cwd)

        return file

    def test_home_prefix(self, file_in_home):
        assert friendly_prefix_for_path(file_in_home) == "~/poems.txt"

    def test_cwd_prefix(self, file_in_cwd):
        assert friendly_prefix_for_path(file_in_cwd) == "./stories.txt"


class TestDeserializeProcedure:
    """Test suite for filesystem.deserialize_procedure_file"""

    def test_deserialize_minimal(self, super_minimal_procedure_file_content):
        procedure = deserialize_procedure_file(super_minimal_procedure_file_content)
        keys_with_values_in_spec = procedure.dict(
            exclude_unset=True, exclude_defaults=True
        ).keys()

        assert len(procedure.steps) == 2, "Every newline-delimited step is counted"
        assert sorted(keys_with_values_in_spec) == ["steps", "title"]

    def test_deserialize_with_simple_context(
        self, procedure_with_context_as_simple_list
    ):
        procedure = deserialize_procedure_file(procedure_with_context_as_simple_list)

        assert len(procedure.context) == 2

    def test_deserialize_with_complex_context(
        self, procedure_with_context_as_list_of_mappings
    ):
        procedure = deserialize_procedure_file(
            procedure_with_context_as_list_of_mappings
        )

        assert len(procedure.context) == 3


class TestProcedureObjectMetadata:
    """Test suite for filesytem.procedure_object_metadata"""

    def test_without_context(self, super_minimal_procedure_file_content):
        procedure = deserialize_procedure_file(super_minimal_procedure_file_content)
        meta = procedure_object_metadata(procedure)

        expected_context_vars = glot["no_context_to_display_placeholder"]

        assert (
            meta["context_vars"] == expected_context_vars
        ), "Unused context message shown when Procedure has no context"

    def test_with_simple_context(self, procedure_with_context_as_simple_list):
        procedure = deserialize_procedure_file(procedure_with_context_as_simple_list)
        meta = procedure_object_metadata(procedure)

        expected_context_vars = ["current_user_name", "what_user_accomplished_today"]

        assert (
            meta["context_vars"] == expected_context_vars
        ), "Var names shown for Procedure with simple context"

    def test_with_compelx_context(self, procedure_with_context_as_list_of_mappings):
        procedure = deserialize_procedure_file(
            procedure_with_context_as_list_of_mappings
        )
        meta = procedure_object_metadata(procedure)

        expected_context_vars = ["name", "fave_snack", "destination"]

        assert (
            meta["context_vars"] == expected_context_vars
        ), "Var names shown for Procedure with complex context"

    def test_step_count(
        self,
        super_minimal_procedure_file_content,
        procedure_with_context_as_list_of_mappings,
    ):
        procedure_1 = deserialize_procedure_file(super_minimal_procedure_file_content)
        procedure_2 = deserialize_procedure_file(
            procedure_with_context_as_list_of_mappings
        )

        assert procedure_object_metadata(procedure_1)["step_count"] == 2
        assert procedure_object_metadata(procedure_2)["step_count"] == 4


class FixturesForCollectFancyListOutput:
    """Fixtures for TestCollectFancyListOutput"""

    @pytest.fixture
    def home_dot_nothing_dir(self, tmp_path):
        dir_ = tmp_path / DOT_NOTHING_DIRECTORY_NAME
        dir_.mkdir(exist_ok=True)
        (dir_ / "go-wild.yaml").touch(exist_ok=True)
        (dir_ / "look-within.yml").touch(exist_ok=True)

        nested = dir_ / "nested"
        nested.mkdir(exist_ok=True)
        (nested / "practice.yml").touch(exist_ok=True)

        return dir_

    @pytest.fixture
    def cwd_dot_nothing_dir(self, home_dot_nothing_dir):
        dir_ = home_dot_nothing_dir.parent / "working_dir" / DOT_NOTHING_DIRECTORY_NAME

        dir_.mkdir(exist_ok=True, parents=True)
        (dir_ / "pasta-from-scratch.yaml").touch(exist_ok=True)

        return dir_

    @pytest.fixture
    def patched_dirs(self, home_dot_nothing_dir, cwd_dot_nothing_dir, monkeypatch):
        monkeypatch.setattr(filesystem, "CWD", cwd_dot_nothing_dir.parent)
        monkeypatch.setattr(filesystem, "HOME", home_dot_nothing_dir.parent)
        monkeypatch.setattr(filesystem, "CWD_DOT_NOTHING_DIR", cwd_dot_nothing_dir)
        monkeypatch.setattr(filesystem, "HOME_DOT_NOTHING_DIR", home_dot_nothing_dir)


class TestCollectFancyListOutput(FixturesForCollectFancyListOutput):
    """Test suite for not.theatrics.collect_fancy_list_input"""

    @pytest.mark.parametrize(
        "from_dir, expected",
        [
            (
                DirectoryChoicesForListCommand.cwd,
                {"cwd": {"./.nothing": ["pasta-from-scratch"]}},
            ),
            (
                DirectoryChoicesForListCommand.home,
                {
                    "home": {
                        "~/.nothing": ["look-within", "go-wild"],
                        "~/.nothing/nested": ["practice"],
                    }
                },
            ),
            (
                DirectoryChoicesForListCommand.both,
                {
                    "cwd": {"./.nothing": ["pasta-from-scratch"]},
                    "home": {
                        "~/.nothing": ["look-within", "go-wild"],
                        "~/.nothing/nested": ["practice"],
                    },
                },
            ),
        ],
    )
    def test_include_options(self, from_dir, expected, patched_dirs):
        procedure_names_by_dir = collect_fancy_list_input(from_dir)

        assert procedure_names_by_dir == expected
