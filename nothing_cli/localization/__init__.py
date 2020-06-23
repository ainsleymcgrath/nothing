"""The localization module provides localized user-facing strings

generally, one need only import the polyglot singleton object

This module uses an unorthodox approach to singletons to avoid keeping
state in the module, which feels more awkward.

When python 3.9 comes out in earnest, revisit using a backport of:
https://www.python.org/dev/peps/pep-0603/ which deals in frozenmappings"""

import ctypes
from json import load
from locale import getdefaultlocale, normalize, windows_locale
from os import getenv
from pathlib import Path
from platform import system
from typing import Dict, NamedTuple, Set, Union

from .constants import DEFAULT_LOCALE, STRINGS_SUPPORTED


class _LocaleConfig(NamedTuple):
    aliases: Set[str]
    filename: str


class _Polyglot(Dict[str, str]):
    """This class is responsible for lazy-loading the best-effort translation of user-facing
    strings."""

    language_mappings = {
        DEFAULT_LOCALE: _LocaleConfig(aliases={"en", "en_US"}, filename="en.json")
    }

    def __init__(self) -> None:
        system_locale = get_system_locale()
        maybe_locale_from_alias_map = (
            k
            for k, v in self.language_mappings.items()
            if system_locale == k or system_locale in v.aliases
        )
        self.locale = next(maybe_locale_from_alias_map, DEFAULT_LOCALE)
        locale_file = (
            Path(__file__).resolve().parent
            / self.language_mappings[self.locale].filename
        )

        with open(locale_file, "rb") as file:
            contents: Dict[str, str] = load(file)
            super(_Polyglot, self).__init__(contents)

    def localized(
        self, key: str, context: Dict[str, Union[int, Union[str, int, object]]]
    ) -> str:
        """Given a key string and context, return formatted localized string"""
        # Pylint believes this isnt a dict because it doesnt _quite_ speak mypy.
        return self.__getitem__(key).format(**context)  # pylint: disable=E1101

    # TODO run this somewhere lol :scream_cat:
    def test(self) -> None:
        """Test if the locfile is complete."""

        missing_entries = [
            entry
            for entry in STRINGS_SUPPORTED
            if entry not in self  # pylint: disable=E1135
        ]
        superfluous_entries = [
            entry
            for entry in self  # pylint: disable=E1133
            if entry not in STRINGS_SUPPORTED
        ]

        if missing_entries:
            raise KeyError(
                f"Missing entries {missing_entries} from {self.locale} locfile."
            )

        if superfluous_entries:
            raise KeyError(
                f"Superfluous entries {superfluous_entries} in {self.locale} locfile."
            )


def get_system_locale() -> str:
    """Attempt to get the UI language defaulting to english. Windows is a little tricky.

    you can override the locale (probably for testing) by setting `NOT_LOCALE`."""

    env_override = getenv("NOT_LOCALE", "")

    if env_override:
        return normalize(str(env_override))

    if system() == "Windows":
        try:
            # The windll property only exists in windows,
            # so this raises a linter concern.
            return normalize(
                windows_locale[
                    ctypes.windll.kernel32
                ].GetUserDefaultUILanguage()  # type: ignore
            )
        except (KeyError, AttributeError, TypeError):
            pass

    system_locale = getdefaultlocale()[0]

    return normalize(system_locale) if system_locale else DEFAULT_LOCALE


# Import this singleton, not the _Polyglot class.
# Pylint is wrong here, this isnt a constant.
polyglot = _Polyglot()  # pylint: disable=C0103
