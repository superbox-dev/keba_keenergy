# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_legacy.py`."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final

from custom_components.keba_keenergy.legacy import LEGACY_STATES

if TYPE_CHECKING:
    from enum import Enum

# The enums with a state of `keba_keenergy_api` 2.x.
LEGACY_ENUMS: Final[list[type[Enum]]] = sorted(
    {type(member) for member in LEGACY_STATES},
    key=lambda enum: enum.__name__,
)
