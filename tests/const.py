# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Constants of the fake KEBA KeEnergy Web HMI, the values of the variants of its responses.

The responses are in `tests/fixtures/`, `fake_api` loads them:

- `common/`: the responses that are the same for every setup (device info, system, HMI, time zone, curves)
- `single_device/`, `multiple_devices/`: the responses of a setup with one or several devices of each type, the
  numbers of the devices (`device_numbers.json`), the values read once on setup (`fixed_data.json`) and the values
  of each update (`data.json`)
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime
from http import HTTPStatus
from typing import Final
from typing import NotRequired
from typing import TypedDict

# The time of the tests, 2026-01-24 13:00 in the time zone of the Web HMI, in the day block of the week timers.
NOW: Final[datetime] = datetime(2026, 1, 24, 12, 0, tzinfo=UTC)


class Attributes(TypedDict):
    """Attributes of a value of the Web HMI, read with `attr` "1"."""

    formatId: NotRequired[str]
    longText: NotRequired[str]
    unitId: NotRequired[str]
    upperLimit: NotRequired[str]
    lowerLimit: NotRequired[str]
    dynUpperLimit: NotRequired[int]
    dynLowerLimit: NotRequired[int]


class ReadValue(TypedDict):
    """Value of a variable in a read response of the Web HMI."""

    name: str
    value: str
    attributes: NotRequired[Attributes]


type Response = list[ReadValue]


class AlarmTimeStamp(TypedDict):
    """Time of an alarm of the Web HMI, the local time of the control unit."""

    year: int
    month: int
    day: int
    hours: int
    minutes: int
    seconds: int


class AlarmValue(TypedDict):
    """Pending alarm in the response of `/alarm?action=getAll` of the Web HMI."""

    alarmNr: int
    compNr: int
    instanceNr: int
    prio: int
    quittable: bool
    shortText: str
    longText: str
    timeStamp: AlarmTimeStamp


# A response of a read request, an `HTTPStatus` fails it with an empty response and an exception is raised.
type ReadResponse = Exception | HTTPStatus | Response


# Suffix of the message ids (`state.msgId`) of the components, read with the values.
MESSAGE_ID_SUFFIX: Final[str] = ".state.msgId"

# The sensors that the second heating circuit and hot water tank do not have, the control unit reports them as
# deactivated.
DEACTIVATED_MESSAGE_IDS: Final[dict[str, int]] = {
    f"APPL.CtrlAppl.sParam.{name}.state.msgId": 10
    for name in (
        "heatCircuit[1].dewPoint",
        "heatCircuit[1].heatCircuitMixer.flowTemp",
        "heatCircuit[1].heatCircuitMixer.mixer",
        "heatCircuit[1].heatCircuitMixer.refluxTemp",
        "heatCircuit[1].humidityRoom",
        "heatCircuit[1].pump",
        "heatCircuit[1].pumpAO",
        "heatCircuit[1].tempReflux",
        "heatCircuit[1].tempRoom",
        "hotWaterTank[1].FreshWater.freshWaterFlow",
        "hotWaterTank[1].FreshWater.freshWaterTemp",
    )
}

# The default block of the week timers of the fake Web HMI, 06:00 to 22:00 as seconds since midnight.
WEEK_TIMER_DAY_START_SECONDS: Final[int] = 21600
WEEK_TIMER_DAY_STOP_SECONDS: Final[int] = 79200

# The remote access of the Web HMI by the action that reads it.
REMOTE_ACCESS: Final[dict[str, bool]] = {
    "isModbusActive": True,
    "isRemoteMActive": False,
    "isRemoteMConnectionAlive": False,
    "isRemoteMServerReachable": True,
}

# The key of the value in the response of the actions that read the remote access.
REMOTE_ACCESS_RESPONSE_KEYS: Final[dict[str, str]] = {
    "isModbusActive": "active",
    "isRemoteMActive": "active",
    "isRemoteMConnectionAlive": "connected",
    "isRemoteMServerReachable": "reachable",
}

# The actions that enable or disable the remote access, with the action that reads it.
REMOTE_ACCESS_ACTIVATIONS: Final[dict[str, str]] = {
    "activateModbus": "isModbusActive",
    "activateRemoteM": "isRemoteMActive",
}

# A sensor break, an error that is not acknowledged.
SENSOR_BREAK_ALARM: Final[AlarmValue] = {
    "alarmNr": 700,
    "compNr": 100,
    "instanceNr": 1,
    "prio": 1,
    "quittable": False,
    "shortText": "Sensor source temperature",
    "longText": "Differential control 1 Diff. Regler 1: Sensor source temperature broken (53 - Sensor break)",
    "timeStamp": {"year": 2026, "month": 10, "day": 28, "hours": 16, "minutes": 53, "seconds": 51},
}

# A tripped high pressure switch, an emergency that must be acknowledged on the control unit.
HIGH_PRESSURE_ALARM: Final[AlarmValue] = {
    "alarmNr": 12,
    "compNr": 200,
    "instanceNr": 2,
    "prio": 0,
    "quittable": True,
    "shortText": "High pressure switch",
    "longText": "Heat pump 2 Wärmepumpe 2: High pressure switch tripped",
    "timeStamp": {"year": 2026, "month": 10, "day": 29, "hours": 7, "minutes": 5, "seconds": 0},
}

# The names of the values that the tests change.
HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET: Final[str] = "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp"

# The values of the setup with one device of each type, which most tests of a single device use.
SINGLE_DEVICE_VALUES: Final[dict[str, str]] = {
    "APPL.CtrlAppl.sParam.extHeatSource[0].values.setTemp": "1",
    "APPL.CtrlAppl.sParam.heatCircuit[0].values.coolRequest": "0",
    HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET: "1.5",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.heatCurveGradient": "0.1",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.coolCurveGradient": "0.1",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.enableHeatCurveLinTab": "true",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.linTab.fileName": "HC1",
    "APPL.CtrlAppl.sParam.hotWaterTank[0].FreshWater.freshWaterFlow.values.actValue": "false",
    "APPL.CtrlAppl.sParam.hotWaterTank[0].circTemp.values.actValue": "30.5",
}

# Passive cooling of the heat pump, a value of the setup with several devices of each type read once on setup.
PASSIVE_COOLING_VALUES: Final[dict[str, str]] = {"APPL.CtrlAppl.sParam.options.heatpump[0].hasPassiveCooling": "true"}

# Other modes and settings of the setup with several devices of each type.
OTHER_MODES_VALUES: Final[dict[str, str]] = {
    "APPL.CtrlAppl.sParam.extHeatSource[1].param.supportExcessEnergy": "false",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode": "4",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.operatingMode": "4",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.heatCurveOffset": "4.5",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.heatCurveOffset": "-4.5",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.coolCurveOffset": "4.5",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.coolCurveOffset": "-4.5",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.heatCurveGradient": "0.69999999",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.heatCurveGradient": "0.80000001",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.coolCurveGradient": "0.69999999",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.coolCurveGradient": "0.80000001",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.linTab.fileName": "HC FBH",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.linTab.fileName": "HC HK",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.coollinTab.fileName": "HC2",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.coollinTab.fileName": "HC2",
    "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[0]": "true",
    "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]": "false",
    "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed": "false",
    "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode": "1",
    "APPL.CtrlAppl.sParam.bufferTank[1].param.operatingMode": "2",
    "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode": "2",
    "APPL.CtrlAppl.sParam.hotWaterTank[1].param.operatingMode": "1",
    "APPL.CtrlAppl.sParam.hotWaterTank[1].circTemp.values.actValue": "36.5",
    "APPL.CtrlAppl.sParam.hotWaterTank[0].circPump.pump.values.setValueB": "false",
    "APPL.CtrlAppl.sParam.hotWaterTank[1].circPump.pump.values.setValueB": "true",
}

# The values of the setup with several devices of each type after an update of the entities.
ENTITY_UPDATED_VALUES: Final[dict[str, str]] = {
    "APPL.CtrlAppl.sParam.extHeatSource[0].param.operatingMode": "1",
    "APPL.CtrlAppl.sParam.extHeatSource[1].param.operatingMode": "0",
    "APPL.CtrlAppl.sParam.extHeatSource[0].values.setTemp": "13",
    "APPL.CtrlAppl.sParam.extHeatSource[1].values.setTemp": "12",
    "APPL.CtrlAppl.sParam.extHeatSource[1].param.supportExcessEnergy": "false",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode": "3",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.heatCurveOffset": "0.5",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.heatCurveOffset": "-0.5",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.coolCurveOffset": "-0.5",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.heatCurveGradient": "0.2",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.heatCurveGradient": "0.30000001",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.coolCurveGradient": "0.2",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.coolCurveGradient": "0.30000001",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.enableHeatCurveLinTab": "true",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.enableHeatCurveLinTab": "false",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.linTab.fileName": "HC2",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.linTab.fileName": "HC3",
    "APPL.CtrlAppl.sParam.heatCircuit[0].param.coollinTab.fileName": "HC4",
    "APPL.CtrlAppl.sParam.heatCircuit[1].param.coollinTab.fileName": "HC4",
    "APPL.CtrlAppl.sParam.solarCircuit[1].values.pump1": "0.67000002",
    "APPL.CtrlAppl.sParam.solarCircuit[0].values.pump2": "0.43000001",
    "APPL.CtrlAppl.sParam.genericHeat[2].referenceTemp.values.actValue": "36.799999",
    "APPL.CtrlAppl.sParam.genericHeat[3].referenceTemp.values.actValue": "26.799999",
    "APPL.CtrlAppl.sParam.genericHeat[1].param.setTempMax.value": "55",
    "APPL.CtrlAppl.sParam.genericHeat[2].param.setTempMax.value": "55",
    "APPL.CtrlAppl.sParam.genericHeat[3].param.setTempMax.value": "55",
    "APPL.CtrlAppl.sParam.genericHeat[2].values.heatRequest": "true",
    "APPL.CtrlAppl.sParam.genericHeat[3].values.heatRequest": "false",
    "APPL.CtrlAppl.sParam.solarCircuit[1].heatMeter.values.power": "3452",
    "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[0]": "true",
    "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]": "false",
    "APPL.CtrlAppl.sParam.bufferTank[0].topTemp.values.actValue": "47.700001",
    "APPL.CtrlAppl.sParam.bufferTank[1].topTemp.values.actValue": "37.700001",
    "APPL.CtrlAppl.sParam.bufferTank[0].midTemp.values.actValue": "25.700001",
    "APPL.CtrlAppl.sParam.bufferTank[1].midTemp.values.actValue": "15.695418",
    "APPL.CtrlAppl.sParam.hotWaterTank[1].values.useExcessEnergy": "2",
    "APPL.CtrlAppl.sParam.hotWaterTank[1].circTemp.values.actValue": "32.5",
    "APPL.CtrlAppl.sParam.hotWaterTank[0].circPump.pump.values.setValueB": "false",
    "APPL.CtrlAppl.sParam.hotWaterTank[1].circPump.pump.values.setValueB": "true",
    "APPL.CtrlAppl.sParam.switchvalve[0].values.actPosition": "1",
    "APPL.CtrlAppl.sParam.switchvalve[1].values.actPosition": "0",
}

# The curve HC1 was renamed on the control unit after the setup, in the names and in the points of the curves.
CURVE_RENAMED_VALUES: Final[dict[str, str]] = {"APPL.CtrlAppl.sParam.linTabPool[0].name": "INVALID"}
