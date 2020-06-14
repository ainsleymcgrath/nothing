# pylint: disable=missing-function-docstring,unused-argument,invalid-name

"""Test fixtures that are shared across suites"""
import json
from typing import List

import pytest


@pytest.fixture(scope="module")
def super_minimal_task_spec_file_content():
    """The bare minimum spec: just a title and newline-delimited steps"""

    yield """---
    title: Set yourself up to be the automation whiz
    steps: |-
        Download Nothing by running this:
        pip install not

        Profit. use the `not` command:
        not do [your boring task]
    """


@pytest.fixture(scope="module")
def task_spec_with_context_as_simple_list():
    """A task spec that uses basic-style context"""

    yield """---
    title: A sample set of do-nothing instructions
    context:
      - current_user_name
      - what_user_accomplished_today
    steps: |-
        Take a good look at yourself, {current_user_name}.

        I heard you accomplished something great today: {what_user_accomplished_today}.
        Give yourself a pat on the back!
    """


@pytest.fixture(scope="module")
def task_spec_with_context_as_list_of_mappings():
    """A task spec that uses mapping-style context"""

    yield """---
    title: Preflight Checks
    context:
      - name: What's your name?
      - fave_snack: What's your favorite snack?
      - destination: Where will you be flying?
    steps: |-
        Check your ticket. Make sure it says {destination}.

        Fasten your seatbelt.
        Don't freak out, {name}.

        There will be {fave_snack} for you, do not worry.
        We have all snacks.

        Enjoy your flight!
    """


@pytest.fixture(scope="module")
def task_spec_with_config_options():
    """A task spec that will override default configuration"""


@pytest.fixture(scope="module")
def task_spec_with_presets():
    """A task spec that utilizes presets"""


@pytest.fixture(scope="module")
def task_spec_using_expressions():
    """A task spec that uses Python expressions inside a template"""


@pytest.fixture(scope="module")
def task_spec_with_everything():
    """A task spec with a value for every optional key"""


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, dict) and isinstance(right, dict) and op == "==":

        def linewise_pretty_dict_strings(d) -> List[str]:
            return json.dumps(d, indent=2).split("\n")

        return [
            "Dictionaries are not equivalent:",
            "",
            "Left:",
            *linewise_pretty_dict_strings(left),
            "",
            "Right:",
            *linewise_pretty_dict_strings(right),
        ]
