# pylint: disable=missing-function-docstring,unused-argument,invalid-name

"""Test fixtures that are shared across suites"""
import json
from typing import List

import pytest


@pytest.fixture(scope="module")
def super_minimal_procedure_file_content():
    """The bare minimum spec: just a title and newline-delimited steps"""

    return """---
    title: Set yourself up to be the automation whiz
    steps: |-
        Download Nothing by running this:
        pip install not

        Profit. use the `not` command:
        not do [your boring task]
    """


@pytest.fixture(scope="module")
def procedure_with_context_as_simple_list():
    """A Procedure that uses basic-style context"""

    return """---
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
def procedure_with_context_as_list_of_mappings():
    """A Procedure that uses mapping-style context"""

    return """---
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
def mixed_context():
    """Some Procedure context using both styles"""

    return """---
    context:
      - deploy_phase
      - raygun_version: What model of raygun do you have?
    """


@pytest.fixture(scope="module")
def procedure_with_knowns():
    """A Procedure that utilizes knowns"""

    return """---
    title: Run away
    knowns:
      - what_to_grab: Everything you own
    steps: |-
        Freak out!!

        Grab {what_to_grab}

        Get out of here!
        Run as fast as you can!!
    """


@pytest.fixture(scope="module")
def procedure_with_lazy_context():
    """A Procedure with a lazy context var"""

    return """---
    title: Get some sleep
    context:
      - __latest_bedtime: What time did you go to sleep last night?

    steps: |-
        Gather all your bedtime supplies

        Last night you went to bed at {__latest_bedtime}...
        You can do better tonight.

        Go to sleep
    """


@pytest.fixture(scope="module")
def procedure_with_everything():
    """A Procedure with a value for every optional key"""


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
