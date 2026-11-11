# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_coordinator.py`."""

from typing import Final

HEAT_CIRCUIT_ENTITY_ID: Final[str] = "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_1"
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
