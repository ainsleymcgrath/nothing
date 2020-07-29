# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test suite for filesystem.collect_fancy_list_input"""

from pathlib import Path
from typing import Dict, List

from ...filesystem import collect_fancy_list_input


def test_only_global_exists(files_in_home: List[Path]):
    result: Dict = collect_fancy_list_input()

    assert "local" not in result
    assert "global" in result


def test_only_local_exists(files_in_cwd: List[Path]):
    result: Dict = collect_fancy_list_input()

    assert "local" in result
    assert "global" not in result


def test_local_and_global_exist(files_in_cwd_and_home: List[Path]):
    result: Dict = collect_fancy_list_input()

    assert "local" in result
    assert "global" in result


def test_no_dot_nothings_exist(empty_dot_nothing_dirs: None):
    result: Dict = collect_fancy_list_input()

    assert result == {}
