# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Static checks of the states of `keba_keenergy_api` 2.x."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from custom_components.keba_keenergy.legacy import get_states
from tests.test_legacy_data import LEGACY_ENUMS

if TYPE_CHECKING:
    from enum import Enum


@pytest.mark.parametrize("enum", LEGACY_ENUMS, ids=[enum.__name__ for enum in LEGACY_ENUMS])
def test_states_are_unique(enum: type[Enum]) -> None:
    """Test that the states of an enum are unique, a selected state must name one member."""
    states: list[str] = get_states(enum)

    assert len(set(states)) == len(states)
