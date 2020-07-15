"""Completion functionality shared across commands in main"""
from itertools import chain
from typing import List

from .constants import CWD_DOT_NOTHING_DIR, HOME_DOT_NOTHING_DIR, PROCEDURE_EXT_PATTERN
from .filesystem import deserialize_procedure_file, glob_each_extension
from .models import Procedure

procedures: List[Procedure] = [
    deserialize_procedure_file(path)
    for path in chain(
        glob_each_extension("*", HOME_DOT_NOTHING_DIR, recurse=True),
        glob_each_extension("*", CWD_DOT_NOTHING_DIR, recurse=True),
    )
]


def procedure_name_completions(incomplete: str):
    """Triggered on [TAB] [TAB] for commands that use it.
    Displays the list of procedures in CWD and home
    along with their descriptions for clatity"""

    for proc in procedures:
        if incomplete in proc.filename:
            yield PROCEDURE_EXT_PATTERN.sub("", proc.filename), f"'{proc.description}'"
