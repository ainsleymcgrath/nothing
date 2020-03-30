from pathlib import Path
from typing import Dict
from tempfile import TemporaryDirectory

import pytest

from .. import utils
from ..constants import NOTHINGFILE_EXTENSION_NAMES, NOTHINGFILE_DIRECTORY_NAME

# TODO: start using the word 'task'
SAMPLE_TASK_NAMES = [
    "code_review_checklist",
    "release_hounds",
    "dazzle_friends",
]


@pytest.fixture(scope="module")
def dir_with_a_file_of_each_extension() -> Dict["str", Path]:

    with TemporaryDirectory() as tempdir:
        for name, extension in zip(SAMPLE_TASK_NAMES, NOTHINGFILE_EXTENSION_NAMES):
            dot_nothings_directory = Path(tempdir) / NOTHINGFILE_DIRECTORY_NAME
            dot_nothings_directory.mkdir(exist_ok=True)

            nothingfile_for_task = dot_nothings_directory / f"{name}.{extension}"

            nothingfile_for_task.touch(exist_ok=True)

        yield tempdir


def test_nothingfile_location_finds_any_extension_under_nothingfile_dir(
    dir_with_a_file_of_each_extension, monkeypatch
):
    def mock_dir():
        return Path(dir_with_a_file_of_each_extension)

    monkeypatch.setattr(Path, "cwd", mock_dir)

    for name in SAMPLE_TASK_NAMES:
        location: Path = utils.nothingfile_location(name)
        assert name in location.name, f"Can locate file for task named {name}"
