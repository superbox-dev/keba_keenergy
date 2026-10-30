# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_coordinator.py`."""

from typing import Final

HEAT_CIRCUIT_ENTITY_ID: Final[str] = "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_1"
# A value of the heating circuits in the body of a read request.
HEAT_CIRCUIT_VALUE: Final[str] = '"APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode"'
