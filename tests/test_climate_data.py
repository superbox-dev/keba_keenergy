# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_climate.py`."""

from typing import Any
from typing import Final

from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import HeatingCircuitRequest
from keba_keenergy_api.enums import HeatPumpState

from tests.api_data import DEFAULT_POSITION_DATA_RESPONSE
from tests.api_data import HEAT_CIRCUIT_COOL_REQUEST
from tests.api_data import HEAT_CIRCUIT_HEAT_REQUEST
from tests.api_data import HEAT_CIRCUIT_OPERATION_MODE
from tests.api_data import replace_values
from tests.api_data import update_response

ENTITY_ID: Final[str] = "climate.keba_keenergy_12345678"
ENTITY_ID_1: Final[str] = "climate.keba_keenergy_12345678_1"
ENTITY_ID_2: Final[str] = "climate.keba_keenergy_12345678_2"


def get_hvac_action_data_response(
    *,
    heat_pump_state: HeatPumpState,
    heat_request: HeatingCircuitRequest = HeatingCircuitRequest.ACTIVE,
    cool_request: HeatingCircuitRequest = HeatingCircuitRequest.OFF,
    operating_mode: HeatingCircuitOperatingMode = HeatingCircuitOperatingMode.REDUCED,
) -> list[dict[str, Any]]:
    """Return the values of a setup with one device of each type, with the requests and the heat pump state."""
    return update_response(
        replace_values(
            DEFAULT_POSITION_DATA_RESPONSE,
            (HEAT_CIRCUIT_OPERATION_MODE, "0", str(operating_mode.value)),
            (HEAT_CIRCUIT_HEAT_REQUEST, "0", str(heat_request.value)),
            (HEAT_CIRCUIT_COOL_REQUEST, "0", str(cool_request.value)),
        ),
        "APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState",
        value=str(heat_pump_state.value),
    )
