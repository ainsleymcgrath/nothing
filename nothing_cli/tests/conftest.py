# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=invalid-name,redefined-outer-name
"""Test fixtures that are shared across suites"""
import json
from pathlib import Path
from typing import Callable, List, Tuple

import pytest

from .. import filesystem, main
from ..filesystem import deserialize_procedure_file
from ..models import Procedure


@pytest.fixture
def patched_filesystem(monkeypatch, tmp_path) -> Tuple[Path, Path]:
    home = tmp_path / "home"
    cwd = tmp_path / "cwd"
    monkeypatch.setattr(filesystem, "HOME", home)
    monkeypatch.setattr(filesystem, "CWD", cwd)

    return home, cwd


@pytest.fixture(autouse=True)
def existing_home_dot_nothing_dir(monkeypatch, patched_filesystem) -> Path:
    dot_nothing = patched_filesystem[0] / ".nothing"
    dot_nothing.mkdir(exist_ok=True, parents=True)
    monkeypatch.setattr(filesystem, "HOME_DOT_NOTHING_DIR", dot_nothing)
    monkeypatch.setattr(main, "HOME_DOT_NOTHING_DIR", dot_nothing)

    return dot_nothing


@pytest.fixture(autouse=True)
def existing_cwd_dot_nothing_dir(monkeypatch, patched_filesystem) -> Path:
    dot_nothing = patched_filesystem[1] / ".nothing"
    dot_nothing.mkdir(exist_ok=True, parents=True)
    monkeypatch.setattr(filesystem, "CWD_DOT_NOTHING_DIR", dot_nothing)
    monkeypatch.setattr(main, "CWD_DOT_NOTHING_DIR", dot_nothing)

    return dot_nothing


@pytest.fixture
def existing_proc_file_path() -> Callable[[Path, str, str], Path]:
    """Helper to take raw yml text, write it to a temporary file, and return the path"""

    def _proc_file_path(parent: Path, filename: str, content: str):
        proc_file = parent / filename
        proc_file.touch()

        with proc_file.open("w") as f:
            f.write(content)

        # "refresh" state each time a proc gets written
        filesystem.state = filesystem.initstate()
        return proc_file

    return _proc_file_path


@pytest.fixture
def existing_proc_instance(
    existing_proc_file_path, existing_cwd_dot_nothing_dir
) -> Callable[[Path, str, str], Procedure]:
    """Helper to take raw yml text, write it to a temporary file, and instantiate
    a Procedure from that file. You probably don't care where it goes, so it
    defaults to CWD. Can be overriden."""

    def _proc_instance(
        filename: str, content: str, parent=existing_cwd_dot_nothing_dir
    ):
        return deserialize_procedure_file(
            existing_proc_file_path(parent, filename, content)
        )

    return _proc_instance


@pytest.fixture
def most_basic_proc():
    """The bare minimum spec: just a title and newline-delimited steps"""

    return (
        "basic.yml",
        """---
    title: Set yourself up to be the automation whiz
    steps: |-
        Download Nothing by running this:
        pip install not

        Profit. use the `not` command:
        not do [your boring task]
    """,
    )


@pytest.fixture
def procedure_with_context_as_simple_list():
    """A Procedure that uses basic-style context"""

    return (
        "simple.yml",
        """---
    title: A sample set of do-nothing instructions
    context:
      - current_user_name
      - what_user_accomplished_today
    steps: |-
        Take a good look at yourself, {current_user_name}.

        I heard you accomplished something great today: {what_user_accomplished_today}.
        Give yourself a pat on the back!
    """,
    )


@pytest.fixture(scope="module")
def procedure_with_context_as_list_of_mappings():
    """A Procedure that uses mapping-style context"""

    return (
        "preflight.yml",
        """---
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
    """,
    )


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

    return (
        "run.yml",
        """---
    title: Run away
    knowns:
      - what_to_grab: Everything you own
    steps: |-
        Freak out!!

        Grab {what_to_grab}

        Get out of here!
        Run as fast as you can!!
    """,
    )


@pytest.fixture(scope="module")
def procedure_with_lazy_context():
    """A Procedure with a lazy context var"""

    return (
        "sleep.yml",
        """---
    title: Get some sleep
    context:
      - __latest_bedtime: What time did you go to sleep last night?

    steps: |-
        Gather all your bedtime supplies

        Last night you went to bed at {__latest_bedtime}...
        You can do better tonight.

        Go to sleep
    """,
    )


@pytest.fixture
def files_in_cwd(
    existing_cwd_dot_nothing_dir: Path,
    existing_proc_file_path: Callable,
    most_basic_proc: Tuple[str, str],
    procedure_with_context_as_list_of_mappings: Tuple[str, str],
    procedure_with_context_as_simple_list: Tuple[str, str],
) -> List[Path]:
    return [
        existing_proc_file_path(existing_cwd_dot_nothing_dir, name, content)
        for (name, content) in [
            most_basic_proc,
            procedure_with_context_as_list_of_mappings,
            procedure_with_context_as_simple_list,
        ]
    ]


@pytest.fixture
def files_in_home(
    existing_home_dot_nothing_dir: Path,
    existing_proc_file_path: Callable,
    procedure_with_lazy_context: Tuple[str, str],
    procedure_with_knowns: Tuple[str, str],
) -> List[Path]:
    return [
        existing_proc_file_path(existing_home_dot_nothing_dir, name, content)
        for (name, content) in [procedure_with_lazy_context, procedure_with_knowns]
    ]


@pytest.fixture
def files_in_cwd_and_home(
    files_in_cwd: List[Path], files_in_home: List[Path]
) -> List[Path]:
    return files_in_cwd + files_in_home


@pytest.fixture
def path_to_simple_basic_proc_file(
    most_basic_proc: Tuple[str, str],
    existing_proc_file_path: Callable,
    existing_cwd_dot_nothing_dir: Path,
) -> Path:
    name, content = most_basic_proc
    return existing_proc_file_path(existing_cwd_dot_nothing_dir, name, content)


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
