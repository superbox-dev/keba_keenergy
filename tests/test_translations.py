# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the translation files."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from typing import Any

import pytest

from tests.test_translations_data import INTEGRATION_DIR
from tests.test_translations_data import STRINGS
from tests.test_translations_data import TRANSLATIONS

if TYPE_CHECKING:
    from pathlib import Path


def _load(path: Path) -> dict[str, Any]:
    """Load a JSON file."""
    content: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return content


def _key_paths(data: dict[str, Any], prefix: str = "") -> set[str]:
    """Return the dotted paths of all texts."""
    paths: set[str] = set()

    for key, value in data.items():
        path: str = f"{prefix}{key}"
        paths |= _key_paths(value, f"{path}.") if isinstance(value, dict) else {path}

    return paths


def _unsorted_keys(data: dict[str, Any], prefix: str = "") -> list[str]:
    """Return the dotted paths of all objects whose keys are not in alphabetical order."""
    unsorted: list[str] = [prefix or "<root>"] if list(data) != sorted(data) else []

    for key, value in data.items():
        if isinstance(value, dict):
            unsorted += _unsorted_keys(value, f"{prefix}{key}.")

    return unsorted


def test_english_translation_identical_to_strings() -> None:
    """Test that `translations/en.json` is identical to `strings.json`."""
    assert (INTEGRATION_DIR / "translations" / "en.json").read_text(encoding="utf-8") == STRINGS.read_text(
        encoding="utf-8",
    )


@pytest.mark.parametrize("path", TRANSLATIONS, ids=lambda path: path.name)
def test_translation_has_all_keys(path: Path) -> None:
    """Test that every translation has exactly the texts of `strings.json`."""
    expected: set[str] = _key_paths(_load(STRINGS))
    actual: set[str] = _key_paths(_load(path))

    assert sorted(expected ^ actual) == []


@pytest.mark.parametrize(
    "path",
    [STRINGS, *TRANSLATIONS, INTEGRATION_DIR / "icons.json"],
    ids=lambda path: path.relative_to(INTEGRATION_DIR).as_posix(),
)
def test_keys_in_alphabetical_order(path: Path) -> None:
    """Test that the keys of every object are in alphabetical order."""
    assert _unsorted_keys(_load(path)) == []
