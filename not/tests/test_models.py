# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument,
# pylint: disable=no-self-use

"""Tests for not.models"""
from typing import Dict

import pytest
from ruamel.yaml import YAML

from ..models import context_items_from_yaml_list, steps_from_yaml_block


yaml = YAML()


class TestContextItemsFromYAMLList:
    """Test suite for not.models.context_items_from_yaml"""

    @pytest.fixture(scope="class")
    def context_objects_from_simple_context_list(
        self, task_spec_with_context_as_simple_list
    ):
        yml: Dict = yaml.load(task_spec_with_context_as_simple_list)

        yield context_items_from_yaml_list(yml["context"])

    def test_with_simple_input(self, context_objects_from_simple_context_list):
        assert len(context_objects_from_simple_context_list) == 2, (
            "A ContextItem object is built for every member "
            "of the context list in the yaml"
        )

        assert not any(
            c.is_complex for c in context_objects_from_simple_context_list
        ), (
            "None of the generated ContextItem objects are complex "
            "when parsing simple context"
        )

    @pytest.fixture(scope="class")
    def context_objects_from_complex_context_list(
        self, task_spec_with_context_as_list_of_mappings
    ):
        yml: Dict = yaml.load(task_spec_with_context_as_list_of_mappings)

        yield context_items_from_yaml_list(yml["context"])

    def test_complex_context(self, context_objects_from_complex_context_list):
        assert len(context_objects_from_complex_context_list) == 3, (
            "A ContextItem object is built for every member "
            "of the context list in the yaml"
        )

        assert all(
            c.is_complex for c in context_objects_from_complex_context_list
        ), "All generated ContextItem objects are complex when parsing complex context"

    def test_mixed_context(self):
        assert 0

    def tes_no_context(self):
        assert (
            context_items_from_yaml_list(None) is None
        ), "When None is passed, None is returned"


class TestStepsFromYAMLBlock:
    """Test suite for not.models.steps_from_yaml_block"""

    @pytest.fixture(scope="class")
    def step_objects_from_simplest_step_block(
        self, super_minimal_task_spec_file_content
    ):
        yml: Dict = yaml.load(super_minimal_task_spec_file_content)

        yield steps_from_yaml_block(yml["steps"])

    def test_simple_steps(self, step_objects_from_simplest_step_block):
        assert (
            len(step_objects_from_simplest_step_block) == 2
        ), "Every newline-delimited step is counted"

        assert all(
            "\n" in step.prompt for step in step_objects_from_simplest_step_block
        ), "Newlines are preserved in serialized steps"

    def test_steps_with_template_values_from_context(self):
        assert 0

    def test_steps_with_template_values_from_presets(self):
        assert 0

    def test_malformed_steps(self):
        assert 0
