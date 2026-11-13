# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_coordinator.py`."""

from typing import Final

HEAT_CIRCUIT_ENTITY_ID: Final[str] = "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_1"
OUTDOOR_TEMPERATURE_ENTITY_ID: Final[str] = "sensor.keba_keenergy_12345678_outdoor_temperature"
# A value of the heating circuits in the body of a read request.
HEAT_CIRCUIT_VALUE: Final[str] = '"APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode"'
REMOTE_MAINTENANCE_SERVER_ENTITY_ID: Final[str] = (
    "binary_sensor.keba_keenergy_12345678_remote_maintenance_server_reachable"
)

# The values of the solar circuits, with their consumers and priorities.
SOLAR_CIRCUIT_SECTIONS: Final[tuple[str, ...]] = (".solarCircuit[", ".genericHeat[", ".hmiRetainData.")

# A setup with several devices of each type, but without solar circuits.
WITHOUT_SOLAR_CIRCUITS_DEVICE_NUMBERS_VALUES: Final[dict[str, str]] = {
    "APPL.CtrlAppl.sParam.options.systemNumberOfSolarCircuits": "0",
}

# The values of the setup without the solar circuits.
WITHOUT_SOLAR_CIRCUITS_VALUES: Final[dict[str, str]] = {
    "APPL.CtrlAppl.sParam.extHeatSource[1].param.supportExcessEnergy": "false",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.operatingMode": "0",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.coolCurveOffset": "1.5",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.coollinTab.fileName": "HC2",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.coollinTab.fileName": "HC2",
}

# The values of the setup without the solar circuits and the heating circuits, which are skipped by their multiplier.
WITHOUT_SOLAR_AND_HEATING_CIRCUITS_VALUES: Final[dict[str, str]] = {
    "APPL.CtrlAppl.sParam.extHeatSource[1].param.supportExcessEnergy": "false",
    "APPL.CtrlAppl.sParam.bufferTank[0].values.setTemp": "42",
}
# A heat meter type and a heat pump state the API doesn't know, e.g. of a newer firmware.
UNKNOWN_HEAT_METER_TYPE: Final[dict[str, str]] = {"APPL.CtrlAppl.sParam.options.heatpump[0].HeatMeter.type": "4"}
UNKNOWN_HEAT_PUMP_STATE: Final[dict[str, str]] = {"APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState": "99"}
# An entity of the heat meter and the entity of the heat pump state.
HEAT_METER_ENTITY_ID: Final[str] = "sensor.keba_keenergy_12345678_heat_pump_heating_power"
HEAT_PUMP_STATE_ENTITY_ID: Final[str] = "sensor.keba_keenergy_12345678_heat_pump_state"
