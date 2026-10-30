# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_select.py`."""

from typing import Final

HEATING_CURVE_ENTITY_ID: Final[str] = "select.keba_keenergy_12345678_heat_circuit_heating_curve_1"
# The options of these selects are the names of the heating curves on the Web HMI, so they are not translated.
CURVE_SELECTS: Final[tuple[str, ...]] = (
    "select.keba_keenergy_12345678_heat_circuit_cooling_curve_2",
    "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
)
