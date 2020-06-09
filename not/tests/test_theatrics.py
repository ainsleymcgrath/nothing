# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument
# pylint: disable=no-self-use

"""Tests for not.theatrics, mostly the private utils"""
from pathlib import Path
import pytest

from ..constants import DirectoryChoicesForListCommand, DOT_NOTHING_DIRECTORY_NAME
from ..theatrics import _collect_fancy_list_input


class FixturesForCollectFancyListOutput:
    """Fixtures for TestCollectFancyListOutput"""

    @pytest.fixture
    def home_dot_nothing_dir(self, tmp_path):
        dir_ = tmp_path / DOT_NOTHING_DIRECTORY_NAME
        dir_.mkdir(exist_ok=True)
        (dir_ / "go-wild.yaml").touch(exist_ok=True)
        (dir_ / "look-within.not").touch(exist_ok=True)

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
    def cwd_dot_not_file_in_subdir(self, cwd_dot_nothing_dir):
        dir_ = cwd_dot_nothing_dir.parent / "nested"

        dir_.mkdir(exist_ok=True)
        (dir_ / "find-yourself.yml").touch(exist_ok=True)

    @pytest.fixture
    def patched_home_and_cwd(
        self,
        home_dot_nothing_dir,
        cwd_dot_nothing_dir,
        cwd_dot_not_file_in_subdir,  # included so this file persists in test filesystem
        monkeypatch,
    ):
        def mock_home():
            return home_dot_nothing_dir.parent

        def mock_cwd():
            return cwd_dot_nothing_dir.parent

        monkeypatch.setattr(Path, "cwd", mock_cwd)
        monkeypatch.setattr(Path, "home", mock_home)


class TestCollectFancyListOutput(FixturesForCollectFancyListOutput):
    """Test suite for not.theatrics._collect_fancy_list_input"""

    @pytest.mark.parametrize(
        "from_dir, expected",
        [
            (
                DirectoryChoicesForListCommand.cwd,
                {
                    "cwd": {
                        "./.nothing": ["pasta-from-scratch"],
                        "./nested": ["find-yourself"],
                    }
                },
            ),
            (
                DirectoryChoicesForListCommand.home,
                {
                    "home": {
                        "~/.nothing": ["go-wild", "look-within"],
                        "~/.nothing/nested": ["practice"],
                    }
                },
            ),
            (
                DirectoryChoicesForListCommand.both,
                {
                    "cwd": {
                        "./.nothing": ["pasta-from-scratch"],
                        "./nested": ["find-yourself"],
                    },
                    "home": {
                        "~/.nothing": ["go-wild", "look-within"],
                        "~/.nothing/nested": ["practice"],
                    },
                },
            ),
        ],
    )
    def test_include_options(self, from_dir, expected, patched_home_and_cwd):
        task_spec_names_by_dir = _collect_fancy_list_input(from_dir)

        assert task_spec_names_by_dir == expected
