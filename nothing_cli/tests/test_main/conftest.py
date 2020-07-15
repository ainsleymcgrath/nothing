# pylint: disable=missing-function-docstring,unused-argument,invalid-name
import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()
