# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument
# pylint: disable=no-self-use

"""Tests for not.theatrics, mostly the private utils"""
import pytest

from .. import filesystem
from .. import theatrics
from ..constants import DirectoryChoicesForListCommand, DOT_NOTHING_DIRECTORY_NAME
from ..theatrics import _collect_fancy_list_input


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

        monkeypatch.setattr(theatrics, "CWD_DOT_NOTHING_DIR", cwd_dot_nothing_dir)
        monkeypatch.setattr(theatrics, "HOME_DOT_NOTHING_DIR", home_dot_nothing_dir)

        monkeypatch.setattr(filesystem, "CWD", cwd_dot_nothing_dir.parent)
        monkeypatch.setattr(filesystem, "HOME", home_dot_nothing_dir.parent)


class TestCollectFancyListOutput(FixturesForCollectFancyListOutput):
    """Test suite for not.theatrics._collect_fancy_list_input"""

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
        task_spec_names_by_dir = _collect_fancy_list_input(from_dir)

        assert task_spec_names_by_dir == expected
