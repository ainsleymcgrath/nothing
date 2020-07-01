# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument
# pylint: disable=no-self-use

"""Tests for not.writer"""
import pytest

from ..constants import FIELD_NAMES_EXCLUDED_FROM_CLEANED_PROCEDURE
from ..models import Step, ProcedureCreate
from ..writer import clean


class TestClean:
    """Test suite for not.writer.clean"""

    @pytest.fixture
    def minimal_procedure(self):
        steps_for_procedure = [
            Step(prompt=prompt, number=i)
            for i, prompt in enumerate(["Get ready!", "Do the thing."])
        ]

        yield ProcedureCreate(
            filename="do-the-thing.yml",
            title="Do The Thing",
            description="How to do the thing",
            steps=steps_for_procedure,
        )

    @pytest.fixture
    def cleaned_minimal_procedure(self, minimal_procedure):
        yield clean(minimal_procedure)

    def test_excluded_fields_are_not_returned(self, cleaned_minimal_procedure):
        assert (
            set(cleaned_minimal_procedure) & FIELD_NAMES_EXCLUDED_FROM_CLEANED_PROCEDURE
            == set()
        ), "No excluded field names make it into he cleaned dict"
