# pylint: disable=missing-function-docstring,unused-argument,invalid-name
"""Test fixtures for test_do"""
from pathlib import Path
from typing import Callable

import pytest
from typer.testing import CliRunner

from ...models import Procedure


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def basic_proc(most_basic_proc: str, existing_proc_instance: Callable) -> Procedure:
    name, content = most_basic_proc
    return existing_proc_instance(name, content)


@pytest.fixture
def proc_with_lazy_context(
    existing_cwd_dot_nothing_dir: Path,
    procedure_with_lazy_context: str,
    existing_proc_instance: Callable,
) -> Procedure:
    name, content = procedure_with_lazy_context
    return existing_proc_instance(name, content)


@pytest.fixture
def proc_with_context(
    procedure_with_context_as_simple_list: str, existing_proc_instance: Callable
) -> Procedure:
    name, content = procedure_with_context_as_simple_list
    return existing_proc_instance(name, content)


@pytest.fixture
def proc_with_knowns(
    procedure_with_knowns: str, existing_proc_instance: Callable
) -> Procedure:
    name, content = procedure_with_knowns
    return existing_proc_instance(name, content)
