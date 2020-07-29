"""Test suite for filesystem.deserialize_procedure_file"""
# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name

from pathlib import Path

from ...filesystem import deserialize_procedure_file
from ...models import Procedure


def test_deserialize_minimal(path_to_simple_basic_proc_file: Path):
    proc = deserialize_procedure_file(path_to_simple_basic_proc_file)

    assert len(proc.steps) == 2, "Every newline-delimited step is counted"


def test_deserialize_with_simple_context(path_to_proc_with_simple_context: Path):
    proc: Procedure = deserialize_procedure_file(path_to_proc_with_simple_context)

    assert len(proc.context) == 2


def test_deserialize_with_complex_context(path_to_proc_with_complex_context):
    proc: Procedure = deserialize_procedure_file(path_to_proc_with_complex_context)

    assert len(proc.context) == 3
