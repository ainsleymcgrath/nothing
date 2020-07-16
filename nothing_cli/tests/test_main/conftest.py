# pylint: disable=missing-function-docstring,unused-argument,invalid-name
"""Test fixtures for test_do"""
import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()
