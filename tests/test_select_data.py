# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_select.py`."""

import json
from typing import Any
from typing import Final

from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_RESPONSE
from tests.api_data import SYSTEM_HEAT_PUMP_NUMBERS
from tests.api_data import get_multiple_devices_fixed_data_response

HEATING_CURVE_ENTITY_ID: Final[str] = "select.keba_keenergy_12345678_heat_circuit_heating_curve_1"
# The options of these selects are the names of the heating curves on the Web HMI, so they are not translated.
CURVE_SELECTS: Final[tuple[str, ...]] = (
    "select.keba_keenergy_12345678_heat_circuit_cooling_curve_2",
    "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
)


def _with_second_heat_pump(values: list[dict[str, Any]], /) -> list[dict[str, Any]]:
    """Return the values with a copy of the values of the first heat pump for a second heat pump."""
    return [
        *values,
        *(
            json.loads(json.dumps(value).replace("heatpump[0]", "heatpump[1]"))
            for value in values
            if "heatpump[0]" in value["name"]
        ),
    ]


# Two heat pumps, only the second one can cool passively, no heating circuit cools.
TWO_HEAT_PUMPS_RESPONSE: Final[list[dict[str, Any]]] = [
    json.loads(SYSTEM_HEAT_PUMP_NUMBERS % "2"),
    *MULTIPLE_DEVICES_RESPONSE[1:],
]
TWO_HEAT_PUMPS_SECOND_PASSIVE_COOLING_FIXED_DATA_RESPONSE: Final[list[dict[str, Any]]] = [
    {**value, "value": "true"} if value["name"].endswith("heatpump[1].hasPassiveCooling") else value
    for value in _with_second_heat_pump(
        get_multiple_devices_fixed_data_response(has_passive_cooling="false", has_cooling_circuits=False),
    )
]
TWO_HEAT_PUMPS_DATA_RESPONSE: Final[list[dict[str, Any]]] = _with_second_heat_pump(MULTIPLE_DEVICES_DATA_RESPONSE)
