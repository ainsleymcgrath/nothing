# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Fixtures shared among the tests in this module"""
from pathlib import Path
from typing import Callable, Tuple

import pytest

from ... import filesystem


@pytest.fixture
def missing_dot_nothing_dirs(
    existing_home_dot_nothing_dir: Path, existing_cwd_dot_nothing_dir: Path
) -> None:
    existing_cwd_dot_nothing_dir.rmdir()
    existing_home_dot_nothing_dir.rmdir()


@pytest.fixture
def empty_dot_nothing_dirs(
    existing_cwd_dot_nothing_dir: Path, existing_home_dot_nothing_dir: Path, monkeypatch
) -> None:
    for path in [
        *existing_cwd_dot_nothing_dir.glob("*"),
        *existing_home_dot_nothing_dir.glob("*"),
    ]:
        path.unlink()

    monkeypatch.setattr(filesystem, "state", filesystem.initstate())


@pytest.fixture
def path_to_proc_with_simple_context(
    procedure_with_context_as_simple_list: Tuple[str, str],
    existing_proc_file_path: Callable,
    existing_cwd_dot_nothing_dir: Path,
) -> Path:
    name, content = procedure_with_context_as_simple_list
    return existing_proc_file_path(existing_cwd_dot_nothing_dir, name, content)


@pytest.fixture
def path_to_proc_with_complex_context(
    procedure_with_context_as_list_of_mappings: Tuple[str, str],
    existing_proc_file_path: Callable,
    existing_cwd_dot_nothing_dir: Path,
) -> Path:
    name, content = procedure_with_context_as_list_of_mappings
    return existing_proc_file_path(existing_cwd_dot_nothing_dir, name, content)


@pytest.fixture
def path_to_proc_with_knowns(
    procedure_with_knowns: Tuple[str, str],
    existing_proc_file_path: Callable,
    existing_cwd_dot_nothing_dir: Path,
) -> Path:
    name, content = procedure_with_knowns
    return existing_proc_file_path(existing_cwd_dot_nothing_dir, name, content)
