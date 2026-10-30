# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_number.py`."""

from typing import Final

# The entities of the setup with one device of each type.
TARGET_TEMPERATURE_OFFSET_ENTITY_ID: Final[str] = "number.keba_keenergy_12345678_heat_circuit_target_temperature_offset"
HEATING_CURVE_SLOPE_ENTITY_ID: Final[str] = "number.keba_keenergy_12345678_heat_circuit_heating_curve_slope"
# The target temperature offset 0.5 of the first heating circuit.
TARGET_TEMPERATURE_OFFSET_WRITE: Final[str] = (
    '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp", "value": "0.5"}]'
)
