# pylint: disable=missing-function-docstring, redefined-outer-name, unused-argument
# pylint: disable=no-self-use

"""Tests for not.theatrics, mostly the private utils"""
import pytest

from .. import filesystem
from .. import theatrics
from ..constants import DirectoryChoicesForListCommand, DOT_NOTHING_DIRECTORY_NAME
from ..filesystem import deserialize_procedure_file
from ..theatrics import _collect_fancy_list_input, InterpolationStore


class FixturesForCollectFancyListOutput:
    """Fixtures for TestCollectFancyListOutput"""

    @pytest.fixture
    def home_dot_nothing_dir(self, tmp_path):
        dir_ = tmp_path / DOT_NOTHING_DIRECTORY_NAME
        dir_.mkdir(exist_ok=True)
        (dir_ / "go-wild.yaml").touch(exist_ok=True)
        (dir_ / "look-within.yml").touch(exist_ok=True)

        nested = dir_ / "nested"
        nested.mkdir(exist_ok=True)
        (nested / "practice.yml").touch(exist_ok=True)

        return dir_

    @pytest.fixture
    def cwd_dot_nothing_dir(self, home_dot_nothing_dir):
        dir_ = home_dot_nothing_dir.parent / "working_dir" / DOT_NOTHING_DIRECTORY_NAME

        dir_.mkdir(exist_ok=True, parents=True)
        (dir_ / "pasta-from-scratch.yaml").touch(exist_ok=True)

        return dir_

    @pytest.fixture
    def patched_dirs(self, home_dot_nothing_dir, cwd_dot_nothing_dir, monkeypatch):

        monkeypatch.setattr(theatrics, "CWD_DOT_NOTHING_DIR", cwd_dot_nothing_dir)
        monkeypatch.setattr(theatrics, "HOME_DOT_NOTHING_DIR", home_dot_nothing_dir)

        monkeypatch.setattr(filesystem, "CWD", cwd_dot_nothing_dir.parent)
        monkeypatch.setattr(filesystem, "HOME", home_dot_nothing_dir.parent)


class TestCollectFancyListOutput(FixturesForCollectFancyListOutput):
    """Test suite for not.theatrics._collect_fancy_list_input"""

    @pytest.mark.parametrize(
        "from_dir, expected",
        [
            (
                DirectoryChoicesForListCommand.cwd,
                {"cwd": {"./.nothing": ["pasta-from-scratch"]}},
            ),
            (
                DirectoryChoicesForListCommand.home,
                {
                    "home": {
                        "~/.nothing": ["look-within", "go-wild"],
                        "~/.nothing/nested": ["practice"],
                    }
                },
            ),
            (
                DirectoryChoicesForListCommand.both,
                {
                    "cwd": {"./.nothing": ["pasta-from-scratch"]},
                    "home": {
                        "~/.nothing": ["look-within", "go-wild"],
                        "~/.nothing/nested": ["practice"],
                    },
                },
            ),
        ],
    )
    def test_include_options(self, from_dir, expected, patched_dirs):
        procedure_names_by_dir = _collect_fancy_list_input(from_dir)

        assert procedure_names_by_dir == expected


class TestInterpolationStore:
    """Test suite for theatrics.InterpolationStore"""

    @pytest.fixture(autouse=True)
    def patched_store(self, monkeypatch):
        def patched_stdin(*_):
            return "sure"

        monkeypatch.setattr(InterpolationStore, "prompt_for_value", patched_stdin)

    @pytest.fixture
    def procedure_with_context_only(self, procedure_with_context_as_list_of_mappings):
        return deserialize_procedure_file(procedure_with_context_as_list_of_mappings)

    def test_get_interpolations(self, procedure_with_context_only):
        store = InterpolationStore(procedure_with_context_only)

        first_step = procedure_with_context_only.steps[0]

        interpolations = store.get_interpolations(first_step)

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
    def procedure_with_knowns_only(self, procedure_with_knowns):
        return deserialize_procedure_file(procedure_with_knowns)

    def test_get_interpolations_knowns(self, procedure_with_knowns_only):
        store = InterpolationStore(procedure_with_knowns_only)

        referencing_step = procedure_with_knowns_only.steps[1]

        interpolations = store.get_interpolations(referencing_step)

        assert interpolations == {
            "what_to_grab": "Everything you own"
        }, "get_interpolations retrieves values that came from knowns"

    def test_get_interpolations_lazy_context(self, procedure_with_lazy_context):
        procedure = deserialize_procedure_file(procedure_with_lazy_context)
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
        interpolations = store.get_interpolations(referencing_step)

        assert interpolations == {"__latest_bedtime": "sure"}, (
            "After calling get_interpolations, the store sets the"
            "lazy contex variable value to the value provided to stdin"
        )
