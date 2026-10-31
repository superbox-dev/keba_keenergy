# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_select.py`."""

from typing import Final

from tests.api_data import HEAT_PUMP_ELECTRIC_ENERGY_METER_TYPE
from tests.api_data import HEAT_PUMP_HAS_ACTIVE_COOLING
from tests.api_data import HEAT_PUMP_HAS_PASSIVE_COOLING
from tests.api_data import HEAT_PUMP_HEAT_METER_TYPE
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_RESPONSE
from tests.api_data import SYSTEM_HEAT_PUMP_NUMBERS
from tests.api_data import Response
from tests.api_data import get_heat_pump_data
from tests.api_data import get_multiple_devices_fixed_data_response
from tests.api_data import replace_values

HEATING_CURVE_ENTITY_ID: Final[str] = "select.keba_keenergy_12345678_heat_circuit_heating_curve_1"
# The options of these selects are the names of the heating curves on the Web HMI, so they are not translated.
CURVE_SELECTS: Final[tuple[str, ...]] = (
    "select.keba_keenergy_12345678_heat_circuit_cooling_curve_2",
    "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
)


# Two heat pumps, only the second one can cool passively, no heating circuit cools.
TWO_HEAT_PUMPS_RESPONSE: Final[Response] = replace_values(MULTIPLE_DEVICES_RESPONSE, SYSTEM_HEAT_PUMP_NUMBERS.read("2"))
TWO_HEAT_PUMPS_SECOND_PASSIVE_COOLING_FIXED_DATA_RESPONSE: Final[Response] = [
    *get_multiple_devices_fixed_data_response(has_passive_cooling="false", has_cooling_circuits=False),
    HEAT_PUMP_HAS_ACTIVE_COOLING.read("false", index=1),
    HEAT_PUMP_HAS_PASSIVE_COOLING.read("true", index=1),
    HEAT_PUMP_ELECTRIC_ENERGY_METER_TYPE.read("2", index=1),
    HEAT_PUMP_HEAT_METER_TYPE.read("2", index=1),
]
TWO_HEAT_PUMPS_DATA_RESPONSE: Final[Response] = [*MULTIPLE_DEVICES_DATA_RESPONSE, *get_heat_pump_data(index=1)]
