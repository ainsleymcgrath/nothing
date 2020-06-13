# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument
# pylint: disable=no-self-use

"""Tests for not.writer"""
import pytest

from ..constants import FIELD_NAMES_EXCLUDED_FROM_CLEANED_TASK_SPEC
from ..models import Step, TaskSpecCreate
from ..writer import clean


class TestClean:
    """Test suite for not.writer.clean"""

    @pytest.fixture
    def minimal_task_spec(self):
        steps_for_task = [
            Step(prompt=prompt, number=i)
            for i, prompt in enumerate(["Get ready!", "Do the thing."])
        ]

        yield TaskSpecCreate(
            filename="do-the-thing.yml",
            title="Do The Thing",
            description="How to do the thing",
            steps=steps_for_task,
        )

    @pytest.fixture
    def cleaned_minimal_task_spec(self, minimal_task_spec):
        yield clean(minimal_task_spec)

    def test_unset_fields_are_not_returned(self, cleaned_minimal_task_spec):
        assert set(cleaned_minimal_task_spec) == {
            "title",
            "steps",
            "context",
            "description",
        }, (
            "The only keys on the dict returned are the ones "
            "explicitly set on the input TaskSpec"
        )

    def test_excluded_fields_are_not_returned(self, cleaned_minimal_task_spec):
        assert (
            set(cleaned_minimal_task_spec) & FIELD_NAMES_EXCLUDED_FROM_CLEANED_TASK_SPEC
            == set()
        ), "No excluded field names make it into he cleaned dict"
