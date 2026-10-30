# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_water_heater.py`."""

from typing import Final

ENTITY_ID: Final[str] = "water_heater.keba_keenergy_12345678"
ENTITY_ID_1: Final[str] = "water_heater.keba_keenergy_12345678_1"
ENTITY_ID_2: Final[str] = "water_heater.keba_keenergy_12345678_2"
ENTITY_ID_3: Final[str] = "water_heater.keba_keenergy_12345678_buffer_tank"
ENTITY_ID_4: Final[str] = "water_heater.keba_keenergy_12345678_buffer_tank_1"
# The tank types in the names of the Web HMI values.
HOT_WATER_TANK: Final[str] = "hotWaterTank"
BUFFER_TANK: Final[str] = "bufferTank"
# The limits of Home Assistant (110 °F and 140 °F) while the Web HMI provides none.
DEFAULT_LIMITS: Final[tuple[float, float]] = (43.3, 60.0)


def get_operating_mode_write(tank: str, operating_mode: int, /) -> str:
    """Return the write request of the operating mode of the first tank of the type (`hotWaterTank`, `bufferTank`)."""
    return f'[{{"name": "APPL.CtrlAppl.sParam.{tank}[0].param.operatingMode", "value": "{operating_mode}"}}]'
