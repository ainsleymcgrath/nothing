# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test suite for filesytem.procedure_location"""

from ...constants import PROCEDURE_EXT
from ...filesystem import procedure_location


def test_doesnt_care_about_extension(path_to_proc_with_simple_context):
    filename = path_to_proc_with_simple_context.name
    plain_name = filename.rstrip(PROCEDURE_EXT)

    assert procedure_location(filename) is not None
    assert procedure_location(filename) == procedure_location(plain_name)


def test_returns_none_for_nonexistent():
    assert procedure_location("secret of life please???") is None
