# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument
# pylint: disable=no-self-use

"""Tests for not.theatrics, mostly the private utils"""
import pytest

from ..theatrics import InterpolationStore


class TestInterpolationStore:
    """Test suite for theatrics.InterpolationStore"""

    @pytest.fixture(autouse=True)
    def patched_store(self, monkeypatch):
        def patched_stdin(*_):
            return "sure"

        monkeypatch.setattr(InterpolationStore, "prompt_for_value", patched_stdin)

    @pytest.fixture
    def procedure_with_context_only(
        self, procedure_with_context_as_list_of_mappings, existing_proc_instance
    ):
        name, content = procedure_with_context_as_list_of_mappings
        return existing_proc_instance(name, content)

    def test_get_interpolations(self, procedure_with_context_only):
        store = InterpolationStore(procedure_with_context_only)

        first_step = procedure_with_context_only.steps[0]

        interpolations = store.get_interpolations(first_step, 1)

        assert interpolations == {
            "destination": "sure"
        }, "The var name from the step maps to the value from stdin"

    @pytest.mark.parametrize(
        "text, expected_names",
        [
            ("welcome to the {venue}", {"venue"}),
            ("the {__thing} is {height} {units} tall", {"height", "units", "__thing"}),
            ("haha", set()),
        ],
    )
    def test_get_format_names(self, text, expected_names, procedure_with_context_only):
        store = InterpolationStore(procedure_with_context_only)
        names = store.get_format_names(text)

        assert names == expected_names

    @pytest.fixture
    def procedure_with_knowns_only(self, procedure_with_knowns, existing_proc_instance):
        name, content = procedure_with_knowns
        return existing_proc_instance(name, content)

    def test_get_interpolations_knowns(self, procedure_with_knowns_only):
        store = InterpolationStore(procedure_with_knowns_only)

        referencing_step = procedure_with_knowns_only.steps[1]

        interpolations = store.get_interpolations(referencing_step, 2)

        assert interpolations == {
            "what_to_grab": "Everything you own"
        }, "get_interpolations retrieves values that came from knowns"

    def test_get_interpolations_lazy_context(
        self, procedure_with_lazy_context, existing_proc_instance
    ):
        name, content = procedure_with_lazy_context
        procedure = existing_proc_instance(name, content)
        store = InterpolationStore(procedure)

        assert "__latest_bedtime" in store.requisite_names, (
            "The store knows it will need the value "
            "for a lazy context variable eventually"
        )

        assert "__latest_bedtime" not in store.store, (
            "The store does not have a value for the lazy context variable "
            "since it has not been requested yet"
        )

        referencing_step = procedure.steps[1]

        # now it reaches to stdin to get the value
        interpolations = store.get_interpolations(referencing_step, 2)

        assert interpolations == {"__latest_bedtime": "sure"}, (
            "After calling get_interpolations, the store sets the"
            "lazy contex variable value to the value provided to stdin"
        )
