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

from tests.const import SINGLE_DEVICE_VALUES

# The heating circuit of the setup with one device of each type and the first one of the setup with several.
HEAT_CIRCUIT_ENTITY_ID: Final[str] = "climate.keba_keenergy_12345678"
HEAT_CIRCUIT_1_ENTITY_ID: Final[str] = "climate.keba_keenergy_12345678_1"
# The selected target temperature of the control unit, without the offset.
SELECTED_TARGET_TEMPERATURE: Final[float] = 20.0
# The selected target temperature 20.0 plus the offset 1.5.
TARGET_TEMPERATURE_WITH_OFFSET: Final[float] = 21.5

# The values of the first heating circuit.
HEAT_CIRCUIT_MODE: Final[str] = "APPL.CtrlAppl.sParam.options.heatCircuit[0].type"
HEAT_CIRCUIT_OPERATION_MODE: Final[str] = "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode"
# The first heating circuit only cools.
COOLING_VALUES: Final[dict[str, str]] = {HEAT_CIRCUIT_MODE: str(HeatingCircuitType.COOLING.value)}
# The night temperature 19.5 of both heating circuits.
NIGHT_TEMPERATURE_VALUES: Final[dict[str, str]] = {
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.reducedSetTemp": "19.5",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.reducedSetTemp": "19.5",
}
# The away date range of one year from today of both heating circuits.
AWAY_DATE_RANGE_VALUES: Final[dict[str, str]] = {
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.start": "1769209200",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.start": "1769209200",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.stop": "1800831599",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.stop": "1800831599",
}

# The first heating circuit heats with the presets sleep and boost.
REDUCED_VALUES: Final[dict[str, str]] = {HEAT_CIRCUIT_OPERATION_MODE: str(HeatingCircuitOperatingMode.REDUCED.value)}
PARTY_VALUES: Final[dict[str, str]] = {HEAT_CIRCUIT_OPERATION_MODE: str(HeatingCircuitOperatingMode.PARTY.value)}
# The first heating circuit follows the schedule or is off.
AUTO_VALUES: Final[dict[str, str]] = {HEAT_CIRCUIT_OPERATION_MODE: str(HeatingCircuitOperatingMode.AUTO.value)}
OFF_VALUES: Final[dict[str, str]] = {HEAT_CIRCUIT_OPERATION_MODE: str(HeatingCircuitOperatingMode.OFF.value)}


def get_hvac_action_values(
    *,
    heat_pump_state: HeatPumpState,
    heat_request: HeatingCircuitRequest = HeatingCircuitRequest.ACTIVE,
    cool_request: HeatingCircuitRequest = HeatingCircuitRequest.OFF,
    operating_mode: HeatingCircuitOperatingMode = HeatingCircuitOperatingMode.REDUCED,
) -> dict[str, str]:
    """Return the values of a setup with one device of each type, with the requests and the heat pump state."""
    return {
        **SINGLE_DEVICE_VALUES,
        HEAT_CIRCUIT_OPERATION_MODE: str(operating_mode.value),
        "APPL.CtrlAppl.sParam.heatCircuit[0].values.heatRequest": str(heat_request.value),
        "APPL.CtrlAppl.sParam.heatCircuit[0].values.coolRequest": str(cool_request.value),
        "APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState": str(heat_pump_state.value),
    }


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


# The heating circuit only cools in the operating mode `AUTO`, the cooling temperatures are 25.0 (day) and 24.0
# (night), the heating temperatures 20.5 and 20.0.
COOLING_SCHEDULE_VALUES: Final[dict[str, str]] = {
    HEAT_CIRCUIT_OPERATION_MODE: "1",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.normalCoolSetTemp": "25",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.reducedCoolSetTemp": "24",
}
