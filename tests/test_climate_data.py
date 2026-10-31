# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_climate.py`."""

from datetime import UTC
from datetime import datetime
from typing import Final

from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import HeatingCircuitRequest
from keba_keenergy_api.enums import HeatingCircuitType
from keba_keenergy_api.enums import HeatPumpState

from tests.api_data import HEAT_CIRCUIT_COOL_REQUEST
from tests.api_data import HEAT_CIRCUIT_HEAT_REQUEST
from tests.api_data import HEAT_CIRCUIT_MODE
from tests.api_data import HEAT_CIRCUIT_OPERATION_MODE
from tests.api_data import HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_DAY
from tests.api_data import HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_NIGHT
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import SINGLE_DEVICE_DATA_RESPONSE
from tests.api_data import SINGLE_DEVICE_FIXED_DATA_RESPONSE
from tests.api_data import SINGLE_DEVICE_RESPONSE
from tests.api_data import ReadResponse
from tests.api_data import Response
from tests.api_data import get_single_device_data_response
from tests.api_data import replace_values
from tests.api_data import update_response

# The heating circuit of the setup with one device of each type and the first one of the setup with several.
HEAT_CIRCUIT_ENTITY_ID: Final[str] = "climate.keba_keenergy_12345678"
HEAT_CIRCUIT_1_ENTITY_ID: Final[str] = "climate.keba_keenergy_12345678_1"
# The selected target temperature of the control unit, without the offset.
SELECTED_TARGET_TEMPERATURE: Final[float] = 20.0
# The selected target temperature 20.0 plus the offset 1.5.
TARGET_TEMPERATURE_WITH_OFFSET: Final[float] = 21.5

# The first heating circuit heats with the presets sleep and boost.
REDUCED_DATA_RESPONSE: Final[Response] = replace_values(
    MULTIPLE_DEVICES_DATA_RESPONSE,
    HEAT_CIRCUIT_OPERATION_MODE.read(str(HeatingCircuitOperatingMode.REDUCED.value)),
)
PARTY_DATA_RESPONSE: Final[Response] = replace_values(
    MULTIPLE_DEVICES_DATA_RESPONSE,
    HEAT_CIRCUIT_OPERATION_MODE.read(str(HeatingCircuitOperatingMode.PARTY.value)),
)
# The first heating circuit follows the schedule or is off.
AUTO_DATA_RESPONSE: Final[Response] = replace_values(
    MULTIPLE_DEVICES_DATA_RESPONSE,
    HEAT_CIRCUIT_OPERATION_MODE.read(str(HeatingCircuitOperatingMode.AUTO.value)),
)
OFF_DATA_RESPONSE: Final[Response] = replace_values(
    MULTIPLE_DEVICES_DATA_RESPONSE,
    HEAT_CIRCUIT_OPERATION_MODE.read(str(HeatingCircuitOperatingMode.OFF.value)),
)


def get_hvac_action_data_response(
    *,
    heat_pump_state: HeatPumpState,
    heat_request: HeatingCircuitRequest = HeatingCircuitRequest.ACTIVE,
    cool_request: HeatingCircuitRequest = HeatingCircuitRequest.OFF,
    operating_mode: HeatingCircuitOperatingMode = HeatingCircuitOperatingMode.REDUCED,
) -> Response:
    """Return the values of a setup with one device of each type, with the requests and the heat pump state."""
    return update_response(
        replace_values(
            SINGLE_DEVICE_DATA_RESPONSE,
            HEAT_CIRCUIT_OPERATION_MODE.read(str(operating_mode.value)),
            HEAT_CIRCUIT_HEAT_REQUEST.read(str(heat_request.value)),
            HEAT_CIRCUIT_COOL_REQUEST.read(str(cool_request.value)),
        ),
        "APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState",
        value=str(heat_pump_state.value),
    )


# The time of the action calls, 2026-01-24 13:00 in the time zone of the Web HMI.
NOW: Final[datetime] = datetime(2026, 1, 24, 12, 0, tzinfo=UTC)
# 2026-01-24 23:00 in the time zone of the Web HMI, outside of the day block of the week timers.
NIGHT: Final[datetime] = datetime(2026, 1, 24, 22, 0, tzinfo=UTC)
# The away date range of one year from today.
AWAY_PRESET_WRITE: Final[str] = (
    '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.start", "value": "1769209200"}, '
    '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.start", "value": "1769209200"}, '
    '{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.stop", "value": "1800831599"}, '
    '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.stop", "value": "1800831599"}]'
)
# The away date range of yesterday, which ends the away mode.
AWAY_DATE_RANGE_RESET_WRITE: Final[str] = (
    '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.start", "value": "1769122800"}, '
    '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.start", "value": "1769122800"}, '
    '{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.stop", "value": "1769209199"}, '
    '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.stop", "value": "1769209199"}]'
)


def get_operating_mode_write(operating_mode: HeatingCircuitOperatingMode, /) -> str:
    """Return the write request of the operating mode of the first heating circuit."""
    return f'[{{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode", "value": "{operating_mode.value}"}}]'


def get_cooling_schedule_responses() -> list[ReadResponse]:
    """Return the responses of a heating circuit that only cools in the operating mode `AUTO`.

    The cooling temperatures are 25.0 (day) and 24.0 (night), the heating temperatures 20.5 and 20.0.
    """
    responses: list[ReadResponse] = get_circuit_type_responses(HeatingCircuitType.COOLING, operating_mode="1")
    data_response: ReadResponse = responses[-1]
    assert isinstance(data_response, list)

    return [
        *responses[:-1],
        replace_values(
            data_response,
            HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_DAY.read("25"),
            HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_NIGHT.read("24"),
        ),
    ]


def get_circuit_type_responses(
    circuit_type: HeatingCircuitType,
    /,
    *,
    operating_mode: str = "3",
) -> list[ReadResponse]:
    """Return the responses of a setup with one device of each type and a heating circuit of the type.

    The operating mode of the heating circuit is `REDUCED` by default.
    """
    return [
        SINGLE_DEVICE_RESPONSE,
        replace_values(SINGLE_DEVICE_FIXED_DATA_RESPONSE, HEAT_CIRCUIT_MODE.read(str(circuit_type.value))),
        replace_values(get_single_device_data_response(), HEAT_CIRCUIT_OPERATION_MODE.read(operating_mode)),
    ]
