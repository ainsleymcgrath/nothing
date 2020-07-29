# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Tests for filesystem.initstate"""
from pathlib import Path
from typing import List

import pytest
from typer import Abort

from ...filesystem import initstate


def test_with_no_files(missing_dot_nothing_dirs: None):
    with pytest.raises(Abort):
        initstate()


def test_default(files_in_cwd_and_home: List[Path]):
    _state = initstate()

    assert set(_state()) == set(files_in_cwd_and_home)


def test_iterator(files_in_cwd_and_home: List[Path]):
    _state = initstate()
    state_iter = _state(iterator=True)

    assert next(state_iter) == _state()[0]
