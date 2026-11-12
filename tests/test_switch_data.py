# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_switch.py`."""

from typing import Final

COMPRESSOR_USE_NIGHT_SPEED_ENTITY_ID: Final[str] = "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed"
SOLAR_PRIORITY_ENTITY_ID: Final[str] = "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_2"
USE_HEATING_CURVE_ENTITY_ID: Final[str] = "switch.keba_keenergy_12345678_heat_circuit_use_heating_curve_1"
USE_COOLING_CURVE_ENTITY_ID: Final[str] = "switch.keba_keenergy_12345678_heat_circuit_use_cooling_curve_2"
MODBUS_ENTITY_ID: Final[str] = "switch.keba_keenergy_12345678_modbus_active"
REMOTE_MAINTENANCE_ENTITY_ID: Final[str] = "switch.keba_keenergy_12345678_remote_maintenance_active"
# The requests of an update of all remote access values.
REMOTE_ACCESS_UPDATE_REQUESTS: Final[list[str]] = [
    "isModbusActive",
    "isRemoteMActive",
    "isRemoteMConnectionAlive",
    "isRemoteMServerReachable",
]
