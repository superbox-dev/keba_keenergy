# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_select.py`."""

from typing import Final

from tests import copy_values
from tests import replace_values
from tests.const import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.const import MULTIPLE_DEVICES_FIXED_DATA_RESPONSE
from tests.const import MULTIPLE_DEVICES_RESPONSE
from tests.const import Response

HEATING_CURVE_ENTITY_ID: Final[str] = "select.keba_keenergy_12345678_heat_circuit_heating_curve_1"
# The options of these selects are the names of the heating curves on the Web HMI, so they are not translated.
CURVE_SELECTS: Final[tuple[str, ...]] = (
    "select.keba_keenergy_12345678_heat_circuit_cooling_curve_2",
    "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
)


# No heating circuit cools and the heat pump cannot cool.
WITHOUT_COOLING_FIXED_DATA_RESPONSE: Final[Response] = replace_values(
    MULTIPLE_DEVICES_FIXED_DATA_RESPONSE,
    {"APPL.CtrlAppl.sParam.options.heatCircuit[1].type": "0"},
)

# Two heat pumps, only the second one can cool passively, no heating circuit cools.
TWO_HEAT_PUMPS_RESPONSE: Final[Response] = replace_values(
    MULTIPLE_DEVICES_RESPONSE,
    {"APPL.CtrlAppl.sParam.options.systemNumberOfHeatPumps": "2"},
)
TWO_HEAT_PUMPS_SECOND_PASSIVE_COOLING_FIXED_DATA_RESPONSE: Final[Response] = [
    *WITHOUT_COOLING_FIXED_DATA_RESPONSE,
    *replace_values(
        copy_values(WITHOUT_COOLING_FIXED_DATA_RESPONSE, ".heatpump[0]", ".heatpump[1]"),
        {"APPL.CtrlAppl.sParam.options.heatpump[1].hasPassiveCooling": "true"},
    ),
]
# The second heat pump has the values of the first one.
TWO_HEAT_PUMPS_DATA_RESPONSE: Final[Response] = [
    *MULTIPLE_DEVICES_DATA_RESPONSE,
    *copy_values(MULTIPLE_DEVICES_DATA_RESPONSE, ".heatpump[0]", ".heatpump[1]"),
]
