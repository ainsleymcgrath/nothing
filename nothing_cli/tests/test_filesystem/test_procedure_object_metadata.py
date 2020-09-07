# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test suite for filesytem.procedure_object_metadata"""

# TODO don't use deserialize here, use the fixture
from ...filesystem import deserialize_procedure_file, procedure_object_metadata


def test_without_context(path_to_simple_basic_proc_file):
    proc = deserialize_procedure_file(path_to_simple_basic_proc_file)
    meta = procedure_object_metadata(proc)

    expected_context_vars = []

    assert (
        meta["context_vars"] == expected_context_vars
    ), "Unused context message shown when Procedure has no context"


def test_with_simple_context(path_to_proc_with_simple_context):
    proc = deserialize_procedure_file(path_to_proc_with_simple_context)
    meta = procedure_object_metadata(proc)

    expected_context_vars = ["current_user_name", "what_user_accomplished_today"]

    assert (
        meta["context_vars"] == expected_context_vars
    ), "Var names shown for Procedure with simple context"


def test_with_compelx_context(path_to_proc_with_complex_context):
    proc = deserialize_procedure_file(path_to_proc_with_complex_context)
    meta = procedure_object_metadata(proc)

    expected_context_vars = ["name", "fave_snack", "destination"]

    assert (
        meta["context_vars"] == expected_context_vars
    ), "Var names shown for Procedure with complex context"


def test_with_knowns(path_to_proc_with_knowns):
    proc = deserialize_procedure_file(path_to_proc_with_knowns)
    meta = procedure_object_metadata(proc)

    expected_knowns = {"what_to_grab": "Everything you own"}

    assert len(meta["knowns"]) == 1
    assert meta["knowns"][0] == expected_knowns


def test_step_count(path_to_simple_basic_proc_file, path_to_proc_with_complex_context):
    proc_1 = deserialize_procedure_file(path_to_simple_basic_proc_file)
    proc_2 = deserialize_procedure_file(path_to_proc_with_complex_context)

    assert procedure_object_metadata(proc_1)["step_count"] == 2
    assert procedure_object_metadata(proc_2)["step_count"] == 4
