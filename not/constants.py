"""Unchanging values that would be inappropriate for config"""
from typing import List, Set

VALID_TASK_SPEC_EXTENSION_NAMES: List = ["yml", "yaml", "not"]
DOT_NOTHING_DIRECTORY_NAME: str = ".nothing"
STEP_SEPARATOR: str = "\n\n"

FIELD_NAMES_EXCLUDED_FROM_CLEANED_TASK_SPEC: Set = {"filename"}
