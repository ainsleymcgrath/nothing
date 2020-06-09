# pylint: disable=missing-function-docstring, redefined-outer-name, not-an-iterable

"""Tests for not.reader"""
from ..models import TaskSpec
from ..reader import deserialize_task_spec_file


def test_serialize_minimal(super_minimal_task_spec_file_content):
    task_spec: TaskSpec = deserialize_task_spec_file(
        super_minimal_task_spec_file_content
    )
    keys_with_values_in_spec = [
        key for key, value in task_spec.dict().items() if value is not None
    ]

    assert len(task_spec.steps) == 2, "Every newline-delimited step is counted"
    assert sorted(keys_with_values_in_spec) == ["steps", "title"]


def test_serialize_with_simple_context(task_spec_with_context_as_simple_list):
    task_spec: TaskSpec = deserialize_task_spec_file(
        task_spec_with_context_as_simple_list
    )

    assert len(task_spec.context) == 2


def test_serialize_with_complex_context(task_spec_with_context_as_list_of_mappings):
    task_spec: TaskSpec = deserialize_task_spec_file(
        task_spec_with_context_as_list_of_mappings
    )

    assert len(task_spec.context) == 3


def test_serialize_extra_config():
    assert 0


def test_serialize_with_presets():
    assert 0
