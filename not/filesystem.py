"""filesystem utilities for not"""
from itertools import chain
from os.path import getatime, getmtime
from pathlib import Path
from time import ctime
from typing import Dict, Iterable, Iterator, List, Union
from typing_extensions import Literal

from ruamel.yaml import YAML

from .constants import (
    DOT_NOTHING_DIRECTORY_NAME,
    TASK_SPEC_EXT_PATTERN,
    VALID_TASK_SPEC_EXTENSION_NAMES,
)
from .localization import polyglot as glot
from .models import (
    ContextItem,
    context_items_from_yaml_list,
    Step,
    steps_from_yaml_block,
    TaskSpec,
)

yaml = YAML()


def glob_each_extension(
    task_spec_name_glob: str, path: Path, recurse=False
) -> Iterator[Path]:
    """For each extention in not.constants.VALID_TASK_SPEC_EXTENSION_NAMES,
    glob for the provided task_spec_name"""

    for ext in VALID_TASK_SPEC_EXTENSION_NAMES:
        glob_str = (
            f"**/{task_spec_name_glob}.{ext}"
            if recurse
            else f"{task_spec_name_glob}.{ext}"
        )
        yield from path.glob(glob_str)


def task_spec_location(task_spec_name: str) -> Union[Path, None]:
    """Take the name of a Task Spec, find the corresponding file, and return its
    canonical location as a path, if it exists"""

    cwd_dot_nothing_dir, home_dot_nothing_dir = (
        path.glob(DOT_NOTHING_DIRECTORY_NAME) for path in [Path.cwd(), Path.home()]
    )

    task_specs_in_home_dot_nothing_dir: Iterator[Path] = chain(
        glob_each_extension(task_spec_name, path) for path in home_dot_nothing_dir
    )

    task_specs_below_cwd_dot_nothing_dir: Iterator[Path] = chain(
        glob_each_extension(task_spec_name, path, recurse=True)
        for path in cwd_dot_nothing_dir
    )

    dot_not_files_below_cwd = Path.cwd().glob(f"**/{task_spec_name}.not")

    any_place_the_task_spec_could_be = chain(
        dot_not_files_below_cwd,
        *task_specs_below_cwd_dot_nothing_dir,
        *task_specs_in_home_dot_nothing_dir,
    )

    return next(any_place_the_task_spec_could_be, None)


def friendly_prefix_for_path(path: Path, location: Literal["home", "cwd"]):
    """Take a long path and return it with a friendly . or ~ where applicable"""

    # TODO ditch the location kwarg, do check if path is child of cwd?
    prefixes_by_location = {glot["home"]: "~", glot["cwd"]: "."}
    verbose_prefix = str(getattr(Path, location)())

    return str(path).replace(verbose_prefix, prefixes_by_location[location])


def task_spec_names_by_parent_dir_name(
    paths: Iterable[Path], base_dir: Literal["home", "cwd"] = None
) -> Dict[str, List[str]]:
    """Helper for theatrics._collect_fancy_list_input.
    Returns a dict with friendly path name keys and lists of friendly task spec
    names as values."""

    accum_dict = {}

    for path in paths:
        if not path.is_file():
            continue

        key = friendly_prefix_for_path(path.parent, base_dir)
        if key in accum_dict:
            accum_dict[key] += [TASK_SPEC_EXT_PATTERN.sub("", path.name)]
            continue

        accum_dict[key] = [TASK_SPEC_EXT_PATTERN.sub("", path.name)]

    return accum_dict


def deserialize_task_spec_file(task_spec_content: str) -> TaskSpec:
    """Take the content of a Task Spec file, try to find the corresponding file,
    return it as a TaskSpec object"""

    yml: Dict = yaml.load(task_spec_content)

    raw_steps = yml.pop("steps")
    raw_context = yml.pop("context", None)

    parsed_steps: List[Step] = steps_from_yaml_block(raw_steps)
    parsed_context: List[ContextItem] = context_items_from_yaml_list(raw_context)

    return TaskSpec(steps=parsed_steps, context=parsed_context, **yml)


def task_spec_file_metadata(file_location: Path) -> Dict:
    """ A dict of:
        full_path
        last_modified
        last_accessed"""

    last_modified = ctime(getmtime(file_location))
    last_accessed = ctime(getatime(file_location))

    return {
        "last_modified": last_modified,
        "last_accessed": last_accessed,
        "full_path": file_location.resolve(),
    }


def task_spec_object_metadata(task_spec: TaskSpec) -> Dict:
    """A dict of:
        title
        step_count
        context_vars"""

    return {
        "title": task_spec.title,
        "step_count": len(task_spec.steps),
        "context_vars": [c.var_name for c in task_spec.context]
        if task_spec.context is not None
        else glot["no_context_to_display_placeholder"],
    }
