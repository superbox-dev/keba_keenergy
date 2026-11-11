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


# No heating circuit cools and the heat pump cannot cool.
WITHOUT_COOLING_VALUES: Final[dict[str, str]] = {"APPL.CtrlAppl.sParam.options.heatCircuit[1].type": "0"}

# Two heat pumps, only the second one can cool passively.
TWO_HEAT_PUMPS_VALUES: Final[dict[str, str]] = {"APPL.CtrlAppl.sParam.options.systemNumberOfHeatPumps": "2"}
SECOND_HEAT_PUMP_PASSIVE_COOLING_VALUES: Final[dict[str, str]] = {
    "APPL.CtrlAppl.sParam.options.heatpump[1].hasPassiveCooling": "true",
}
