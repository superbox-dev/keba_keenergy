# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Fake responses of the KEBA KeEnergy Web HMI for the tests."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from http import HTTPStatus
from typing import Final
from typing import NotRequired
from typing import TypedDict


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
# A response of a read request, an `HTTPStatus` fails it with an empty response and an exception is raised.
type ReadResponse = Exception | HTTPStatus | Response


@dataclass(frozen=True, kw_only=True)
class Variable:
    """Variable of the Web HMI, `{index}` in the name is replaced by the index of the device."""

    name: str
    attributes: Attributes | None = None

    def read(self, value: str, /, *, index: int = 0) -> ReadValue:
        """Return the value of the variable of the device with the index, as the Web HMI responds it."""
        read_value: ReadValue = {"name": self.name.format(index=index), "value": value}

        if self.attributes is not None:
            read_value["attributes"] = self.attributes

        return read_value

    def read_all(self, *values: str) -> Response:
        """Return the values of the variable of the devices, one value per device in the order of their index."""
        return [self.read(value, index=index) for index, value in enumerate(values)]


# Suffix of the message ids (`state.msgId`) of the components, read with the values.
MESSAGE_ID_SUFFIX: Final[str] = ".state.msgId"


def replace_values(response: Response, /, *values: ReadValue) -> Response:
    """Return a copy of the response with other values, e.g. `HEAT_CIRCUIT_OPERATION_MODE.read("4", index=1)`."""
    replaced: dict[str, ReadValue] = {value["name"]: value for value in values}
    assert replaced.keys() <= {value["name"] for value in response}, "every replaced value is in the response"
    return [replaced.get(value["name"], value) for value in response]


def update_response(
    response: Response,
    name: str,
    /,
    *,
    value: str | None = None,
    attributes: Attributes | None = None,
) -> Response:
    """Return a copy of the response, in which the value with the name has the other value or attributes."""
    updated: Response = deepcopy(response)
    values: Response = [read_value for read_value in updated if read_value["name"] == name]
    assert len(values) == 1, f"{name} is not in the response"

    if value is not None:
        values[0]["value"] = value

    if attributes is not None:
        values[0]["attributes"] = attributes

    return updated


EXTERNAL_HEAT_SOURCE_OPERATING_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].param.operatingMode",
    attributes={
        "formatId": "fmtExternalSourceType",
        "longText": "Oper. mode",
        "unitId": "Enum",
        "upperLimit": "2",
        "lowerLimit": "0",
    },
)

EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].values.setTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Temp. nom.",
        "unitId": "Temp",
        "upperLimit": "90",
        "lowerLimit": "20",
    },
)

EXTERNAL_HEAT_SOURCE_HEAT_REQUEST: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].DO.values.setValueB",
)

EXTERNAL_HEAT_SOURCE_OPERATING_TIME: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].DO.operationalData.operationalTimeS",
)

EXTERNAL_HEAT_SOURCE_MAX_RUNTIME: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].DO.operationalData.maxRunTimeS",
)

EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].DO.operationalData.activationCounter",
)

EXTERNAL_HEAT_SOURCE_USE_EXCESS_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].param.supportExcessEnergy",
)

EXTERNAL_HEAT_SOURCE_MIN_RUNTIME_EXCESS_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].param.minRunTimeExcessEnergy",
    attributes={
        "formatId": "fmt3p0",
        "longText": "Min runtime excess e.",
        "unitId": "TimeMin",
        "upperLimit": "10800",
        "lowerLimit": "0",
    },
)

EXTERNAL_HEAT_SOURCE_CONSUMING_EXCESS_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].values.consumingExcessEnergy",
)

EXTERNAL_HEAT_SOURCE_EXCESS_ENERGY_OPERATING_TIME: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].operationalDataExcessEnergy.operationalTimeS",
)

EXTERNAL_HEAT_SOURCE_EXCESS_ENERGY_MAX_RUNTIME: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].operationalDataExcessEnergy.maxRunTimeS",
)

EXTERNAL_HEAT_SOURCE_EXCESS_ENERGY_ACTIVATION_COUNTER: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].operationalDataExcessEnergy.activationCounter",
)

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

HEAT_CIRCUIT_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.heatCircuit[{index}].type",
    attributes={
        "formatId": "fmtHeatCircuitMode",
        "longText": "Mode",
        "unitId": "Enum",
        "upperLimit": "3",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_ROOM_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].tempRoom.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Room temp. act.",
        "unitId": "Temp",
        "upperLimit": "80",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_ROOM_HUMIDITY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].humidityRoom.values.actValue",
    attributes={
        "formatId": "fmt3p0",
        "longText": "Room humidity act.",
        "unitId": "Pct",
        "upperLimit": "100",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_DEW_POINT: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].dewPoint.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Dew Point",
        "unitId": "Temp",
        "upperLimit": "50.0",
        "lowerLimit": "-20.0",
    },
)

HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].values.flowSetTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Nominal temp.",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_MIXER_FLOW_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].heatCircuitMixer.flowTemp.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Inflow temp. act.",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_MIXER_RETURN_FLOW_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].heatCircuitMixer.refluxTemp.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Reflux temp. act.",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_MIXER_POSITION: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].heatCircuitMixer.mixer.values.setValueScaled",
    attributes={
        "formatId": "fmt3p0",
        "longText": "Mixer nom. value",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "-1",
    },
)

HEAT_CIRCUIT_PUMP_STATE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].pump.values.setValueB",
)

HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].tempReflux.values.actValue",
)

HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.normalSetTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Room temp. Day",
        "unitId": "Temp",
        "upperLimit": "30",
        "lowerLimit": "10",
    },
)

HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_DAY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.normalCoolSetTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Room temp. Day",
        "unitId": "Temp",
        "upperLimit": "30",
        "lowerLimit": "10",
    },
)

HEAT_CIRCUIT_HEATING_LIMIT_DAY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.thresholdDayTemp.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Heating limit Day",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-20",
    },
)

HEAT_CIRCUIT_COOLING_LIMIT_DAY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.thresholdDayCoolTemp.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Heating limit Day",
        "lowerLimit": "-20",
        "unitId": "Temp",
        "upperLimit": "100",
    },
)

HEAT_CIRCUIT_EXCESS_ENERGY_HEATING_LIMIT_DAY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.excessEnergy.thresholdDayTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Heating limit day",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-20",
    },
)

HEAT_CIRCUIT_EXCESS_ENERGY_COOLING_LIMIT_DAY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.excessEnergy.thresholdDayCoolTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Cooling limit day",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-20",
    },
)

HEAT_CIRCUIT_HEAT_REQUEST: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].values.heatRequest",
    attributes={
        "formatId": "fmtReqInfo",
        "longText": "Heat request",
        "unitId": "Enum",
        "upperLimit": "6",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_COOL_REQUEST: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].values.coolRequest",
    attributes={
        "formatId": "fmtReqInfo",
        "longText": "Cool request",
        "unitId": "Enum",
        "upperLimit": "6",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.holidaySetTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Room temp. Vacation",
        "unitId": "Temp",
        "upperLimit": "30",
        "lowerLimit": "10",
    },
)

HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.reducedSetTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Room temp. night",
        "unitId": "Temp",
        "upperLimit": "30",
        "lowerLimit": "10",
    },
)

HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_NIGHT: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.reducedCoolSetTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Room temp. Night",
        "unitId": "Temp",
        "upperLimit": "30",
        "lowerLimit": "10",
    },
)

HEAT_CIRCUIT_HEATING_LIMIT_NIGHT: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.thresholdNightTemp.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Heat limit Night",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-20",
    },
)

HEAT_CIRCUIT_COOLING_LIMIT_NIGHT: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.thresholdNightCoolTemp.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Cooling limit night",
        "unitId": "Temp",
        "upperLimit": "40",
        "lowerLimit": "-20",
    },
)

HEAT_CIRCUIT_EXCESS_ENERGY_HEATING_LIMIT_NIGHT: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.excessEnergy.thresholdNightTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Cooling limit night",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-20",
    },
)

HEAT_CIRCUIT_EXCESS_ENERGY_COOLING_LIMIT_NIGHT: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.excessEnergy.thresholdNightCoolTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Cooling limit night",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-20",
    },
)

HEAT_CIRCUIT_OPERATION_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.operatingMode",
    attributes={
        "formatId": "fmtHcMode",
        "longText": "Operating mode",
        "unitId": "Enum",
        "upperLimit": "32767",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_SELECTED_TARGET_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].values.selectedSetTemp",
)

HEAT_CIRCUIT_TARGET_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].values.setValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Room temp. Nom.",
        "unitId": "Temp",
        "upperLimit": "90",
        "lowerLimit": "10",
    },
)

HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.offsetRoomTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Room temp. Offset",
        "unitId": "TempRel",
        "upperLimit": "2.5",
        "lowerLimit": "-2.5",
    },
)

HEAT_CIRCUIT_USE_EXCESS_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.excessEnergy.useExcessEnergy",
)

HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.excessEnergyTemp.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Set heat temp.",
        "unitId": "Temp",
        "upperLimit": "30",
        "lowerLimit": "10",
    },
)

HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.excessEnergyTemp.hyst",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Hyst. heat temp.",
        "unitId": "TempRel",
        "upperLimit": "2",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_COOLING_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.excessEnergyTempCool.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Set cool temp.",
        "unitId": "Temp",
        "upperLimit": "30",
        "lowerLimit": "10",
    },
)

HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_COOLING_TEMPERATURE_HYSTERESIS: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.excessEnergyTempCool.hyst",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Hyst. cool temp.",
        "unitId": "TempRel",
        "upperLimit": "2",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_EXCESS_ENERGY_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].values.useExcessEnergy",
    attributes={
        "formatId": "fmtExcessEnergyInfo",
        "longText": "Excess energy HC 1",
        "unitId": "Enum",
        "upperLimit": "2",
        "lowerLimit": "0",
    },
)

HEAT_CIRCUIT_AWAY_START_DATE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.holiday.start",
    attributes={"formatId": "fmt3p2", "unitId": "TimeHour", "upperLimit": "86400", "lowerLimit": "0"},
)

HEAT_CIRCUIT_AWAY_END_DATE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.holiday.stop",
    attributes={"formatId": "fmt3p2", "unitId": "TimeHour", "upperLimit": "86400", "lowerLimit": "0"},
)

HEAT_CIRCUIT_HEATING_CURVE_OFFSET: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.heatCurveOffset",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Heat curve offset",
        "unitId": "TempRel",
        "upperLimit": "10",
        "lowerLimit": "-10",
    },
)

HEAT_CIRCUIT_COOLING_CURVE_OFFSET: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.coolCurveOffset",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Cool curve offset",
        "unitId": "TempRel",
        "upperLimit": "10",
        "lowerLimit": "-10",
    },
)

HEAT_CIRCUIT_HEATING_CURVE_SLOPE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.heatCurveGradient",
    attributes={"formatId": "fmt3p2", "longText": "Heat curve grad.", "upperLimit": "5", "lowerLimit": "0"},
)

HEAT_CIRCUIT_COOLING_CURVE_SLOPE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.coolCurveGradient",
    attributes={"formatId": "fmt3p2", "longText": "Cool curve grad.", "upperLimit": "5", "lowerLimit": "0"},
)

HEAT_CIRCUIT_USE_HEATING_CURVE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.enableHeatCurveLinTab",
)

HEAT_CIRCUIT_HEATING_CURVE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.linTab.fileName",
)

HEAT_CIRCUIT_COOLING_CURVE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].param.coollinTab.fileName",
)

HEAT_CIRCUIT_PUMP_SPEED: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatCircuit[{index}].pumpAO.values.setValueScaled",
    attributes={
        "formatId": "fmt3p0",
        "longText": "Pump speed",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "0",
    },
)

SOLAR_CIRCUIT_OPERATION_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.solarCircuit[{index}].param.operatingMode",
    attributes={
        "formatId": "fmtSolarOpMode",
        "longText": "Oper. mode",
        "unitId": "Enum",
        "upperLimit": "32767",
        "lowerLimit": "0",
    },
)

SOLAR_CIRCUIT_SOURCE_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.solarCircuit[{index}].collectorTemp.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Source temp.",
        "unitId": "Temp",
        "upperLimit": "90",
        "lowerLimit": "20",
    },
)

SOLAR_CIRCUIT_PUMP_1: Final = Variable(
    name="APPL.CtrlAppl.sParam.solarCircuit[{index}].values.pump1",
    attributes={"formatId": "fmt3p0", "longText": "Pump 1", "unitId": "Pct100", "upperLimit": "1", "lowerLimit": "0.0"},
)

SOLAR_CIRCUIT_PUMP_2: Final = Variable(
    name="APPL.CtrlAppl.sParam.solarCircuit[{index}].values.pump2",
    attributes={"formatId": "fmt3p0", "longText": "Pump 2", "unitId": "Pct100", "upperLimit": "1", "lowerLimit": "0.0"},
)

SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1: Final = Variable(
    name="APPL.CtrlAppl.sParam.genericHeat[{index}].referenceTemp.values.actValue",
)

SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2: Final = Variable(
    name="APPL.CtrlAppl.sParam.genericHeat[{index}].referenceTemp.values.actValue",
)

SOLAR_CIRCUIT_TARGET_TEMPERATURE_1: Final = Variable(
    name="APPL.CtrlAppl.sParam.genericHeat[{index}].param.setTempMax.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Temp. nom. 1",
        "unitId": "Temp",
        "upperLimit": "90",
        "lowerLimit": "0",
    },
)

SOLAR_CIRCUIT_TARGET_TEMPERATURE_2: Final = Variable(
    name="APPL.CtrlAppl.sParam.genericHeat[{index}].param.setTempMax.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Temp. nom. 2",
        "unitId": "Temp",
        "upperLimit": "90",
        "lowerLimit": "0",
    },
)

SOLAR_CIRCUIT_HEAT_REQUEST: Final = Variable(
    name="APPL.CtrlAppl.sParam.genericHeat[{index}].values.heatRequest",
    attributes={"unitId": "Enum", "upperLimit": "6", "lowerLimit": "0"},
)

SOLAR_CIRCUIT_HEATING_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.solarCircuit[{index}].heatMeter.values.accumulatedHeat",
    attributes={
        "formatId": "fmt6p0",
        "longText": "Heat quantity",
        "unitId": "kWh",
        "upperLimit": "900000",
        "lowerLimit": "0",
    },
)

SOLAR_CIRCUIT_DAILY_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.solarCircuit[{index}].heatMeter.values.heatDay",
)

SOLAR_CIRCUIT_ACTUAL_POWER: Final = Variable(
    name="APPL.CtrlAppl.sParam.solarCircuit[{index}].heatMeter.values.power",
)

SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2: Final = Variable(
    name="APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[{index}]",
)

HEAT_PUMP_CONSUMING_EXCESS_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].values.consumingExcessEnergy",
)

HEAT_PUMP_EXCESS_ENERGY_OPERATING_TIME: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].operationalDataExcessEnergy.operationalTimeS",
)

HEAT_PUMP_EXCESS_ENERGY_MAX_RUNTIME: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].operationalDataExcessEnergy.maxRunTimeS",
)

HEAT_PUMP_EXCESS_ENERGY_ACTIVATION_COUNTER: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].operationalDataExcessEnergy.activationCounter",
)

HEAT_PUMP_CIRCULATION_PUMP_SPEED: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].CircPump.values.setValueScaled",
    attributes={
        "formatId": "fmt3p0",
        "longText": "Circulation pump",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "0.0",
    },
)

HEAT_PUMP_SOURCE_PUMP_SPEED: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].Source.values.setValueScaled",
    attributes={"formatId": "fmt3p0", "longText": "Source", "unitId": "Pct100", "upperLimit": "1", "lowerLimit": "0.0"},
)

HEAT_PUMP_COMPRESSOR: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].Compressor.values.setValueScaled",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Compressor",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "0.0",
    },
)

HEAT_PUMP_COMPRESSOR_NIGHT_SPEED: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].HeatPumpPowerCtrl.param.maxPowerScaledNight",
    attributes={
        "formatId": "fmt3p0",
        "longText": "Max. pwr. limit night",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "0.5",
    },
)

HEAT_PUMP_COMPRESSOR_INPUT_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].TempCompressorIn.values.actValue",
)

HEAT_PUMP_COMPRESSOR_OUTPUT_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].TempCompressorOut.values.actValue",
)


HEAT_PUMP_COMPRESSOR_USE_NIGHT_SPEED: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].HeatPumpPowerCtrl.param.useDayNightSpeed",
)

HEAT_PUMP_CONDENSER_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].OverHeatCtrl.values.tempCond",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Cond. temp.",
        "unitId": "Temp",
        "upperLimit": "200",
        "lowerLimit": "0",
    },
)

HEAT_PUMP_VAPORIZER_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].OverHeatCtrl.values.tempVap",
)

HEAT_PUMP_TARGET_OVERHEATING: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].OverHeatCtrl.values.setOH",
)

HEAT_PUMP_CURRENT_OVERHEATING: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].OverHeatCtrl.values.actOH",
)

HEAT_PUMP_EXPANSION_VALVE_POSITION: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].OverHeatCtrl.values.stepperPos",
)

HEAT_PUMP_HEAT_REQUEST: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].values.request",
)

HEAT_PUMP_HIGH_PRESSURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].HighPressure.values.actValue",
)

HEAT_PUMP_LOW_PRESSURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].LowPressure.values.actValue",
)

HEAT_PUMP_FLOW_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].TempHeatFlow.values.actValue",
)

HEAT_PUMP_RETURN_FLOW_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].TempHeatReflux.values.actValue",
)

HEAT_PUMP_NAME: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].param.name",
)

HEAT_PUMP_SOURCE_INPUT_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].TempSourceIn.values.actValue",
)

HEAT_PUMP_SOURCE_OUTPUT_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].TempSourceOut.values.actValue",
)

HEAT_PUMP_STATE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].values.heatpumpState",
    attributes={
        "formatId": "fmtHPState",
        "longText": "State",
        "unitId": "Enum",
        "upperLimit": "32767",
        "lowerLimit": "0",
    },
)

HEAT_PUMP_SUBSTATE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].values.heatpumpSubState",
    attributes={
        "formatId": "fmtHPSubState",
        "longText": "Substate",
        "unitId": "Enum",
        "upperLimit": "32767",
        "lowerLimit": "0",
    },
)

HEAT_PUMP_COMPRESSOR_POWER: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].ElectricEnergyMeter.values.power",
)

HEAT_PUMP_HEATING_POWER: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].HeatMeter.values.power",
)

HEAT_PUMP_HOT_WATER_POWER: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].HotWaterMeter.values.power",
)

HEAT_PUMP_COP: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].values.COP",
)

HEAT_PUMP_HEATING_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.heating.energy",
)

HEAT_PUMP_HEATING_ENERGY_CONSUMPTION: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.heating.electricalenergy",
)

HEAT_PUMP_HEATING_SPF: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].EnergyEfficiencyRatioHeat",
)

HEAT_PUMP_COOLING_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.cooling.energy",
)

HEAT_PUMP_COOLING_ENERGY_CONSUMPTION: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.cooling.electricalenergy",
)

HEAT_PUMP_COOLING_SPF: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].EnergyEfficiencyRatioCool",
)

HEAT_PUMP_HOT_WATER_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.domHotWater.energy",
)

HEAT_PUMP_HOT_WATER_ENERGY_CONSUMPTION: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.domHotWater.electricalenergy",
)

HEAT_PUMP_HOT_WATER_SPF: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].EnergyEfficiencyRatioDomHotWater",
)

HEAT_PUMP_TOTAL_THERMAL_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.energy",
)

HEAT_PUMP_TOTAL_ENERGY_CONSUMPTION: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.electricalenergy",
)

HEAT_PUMP_TOTAL_SPF: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].EnergyEfficiencyRatio",
)

HEAT_PUMP_EXCESS_ENERGY_CONSUMPTION: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.consumedExcessEnergy",
)

HEAT_PUMP_HEATING_EXCESS_ENERGY_CONSUMPTION: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.heating.consumedExcessEnergy",
)

HEAT_PUMP_COOLING_EXCESS_ENERGY_CONSUMPTION: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.cooling.consumedExcessEnergy",
)

HEAT_PUMP_HOT_WATER_EXCESS_ENERGY_CONSUMPTION: Final = Variable(
    name="APPL.CtrlAppl.sStatisticalData.heatpump[{index}].consumption.domHotWater.consumedExcessEnergy",
)

HEAT_PUMP_OPERATING_TIME: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].operationalData.operationalTimeS",
)


HEAT_PUMP_MAX_RUNTIME: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].operationalData.maxRunTimeS",
)


HEAT_PUMP_ACTIVATION_COUNTER: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].operationalData.activationCounter",
)

HEAT_PUMP_HAS_COMPRESSOR_FAILURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].FailureCompressor.values.actValue",
)

HEAT_PUMP_HAS_SOURCE_FAILURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].FailureSource.values.actValue",
)

HEAT_PUMP_HAS_SOURCE_ACTUATOR_FAILURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].FailureActuatorSource.values.actValue",
)

HEAT_PUMP_HAS_THREE_PHASE_FAILURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].FailureThreePhase.values.actValue",
)

HEAT_PUMP_HAS_SOURCE_PRESSURE_FAILURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].FailureSrcPressure.values.actValue",
)

HEAT_PUMP_HAS_VFD_FAILURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.heatpump[{index}].FailureVFD.values.actValue",
)

HEAT_PUMP_HAS_ACTIVE_COOLING: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.heatpump[{index}].hasActiveCooling",
)

HEAT_PUMP_HAS_PASSIVE_COOLING: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.heatpump[{index}].hasPassiveCooling",
)

EXTERNAL_HEAT_SOURCE_HAS_EMISSIONS: Final = Variable(
    name="APPL.CtrlAppl.sParam.extHeatSource[{index}].param.hasEmmission",
)

HEAT_PUMP_ELECTRIC_ENERGY_METER_TYPE: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.heatpump[{index}].ElectricEnergyMeter.type",
    attributes={
        "formatId": "fmtElMeterType",
        "longText": "El. energy meter",
        "unitId": "Enum",
        "upperLimit": "4",
        "lowerLimit": "0",
    },
)

HEAT_PUMP_HEAT_METER_TYPE: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.heatpump[{index}].HeatMeter.type",
    attributes={
        "formatId": "fmtHeatMeterType",
        "longText": "Heat meter",
        "unitId": "Enum",
        "upperLimit": "4",
        "lowerLimit": "0",
    },
)

BUFFER_TANK_CURRENT_TOP_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].topTemp.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Temp. top act.",
        "unitId": "Temp",
        "upperLimit": "90",
        "lowerLimit": "5",
    },
)

BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].midTemp.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Temp. bottom act.",
        "unitId": "Temp",
        "upperLimit": "90",
        "lowerLimit": "5",
    },
)

BUFFER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].param.excessEnergyTemp.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Set heat temp.",
        "unitId": "Temp",
        "upperLimit": "95",
        "lowerLimit": "0",
    },
)

BUFFER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].param.excessEnergyTemp.hyst",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Hyst. heat temp.",
        "unitId": "TempRel",
        "upperLimit": "5",
        "lowerLimit": "0",
    },
)

BUFFER_TANK_EXCESS_ENERGY_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].values.useExcessEnergy",
    attributes={
        "formatId": "fmtExcessEnergyInfo",
        "longText": "Excess energy buffer 1",
        "unitId": "Enum",
        "upperLimit": "2",
        "lowerLimit": "0",
    },
)

BUFFER_TANK_OPERATING_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].param.operatingMode",
    attributes={
        "formatId": "fmtBufferMode",
        "longText": "Oper. mode",
        "unitId": "Enum",
        "upperLimit": "32767",
        "lowerLimit": "0",
    },
)

BUFFER_TANK_STANDBY_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].param.backupTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Backup temp.",
        "unitId": "Temp",
        "upperLimit": "90",
        "lowerLimit": "0",
    },
)

BUFFER_TANK_TARGET_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].values.setTemp",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Set temp.",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "0",
    },
)

BUFFER_TANK_HEAT_REQUEST: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].values.heatRequestTop",
)

BUFFER_TANK_COOL_REQUEST: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].values.coolRequestBot",
)

BUFFER_TANK_USE_EXCESS_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].param.useExcessEnergy",
)

BUFFER_TANK_OUTDOOR_TEMPERATURE_EXCESS_ENERGY_LIMIT: Final = Variable(
    name="APPL.CtrlAppl.sParam.bufferTank[{index}].param.thresholdOutTempExcessEnergy.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Au\u00dfentemp. \u00dcE Grenze",
        "unitId": "Temp",
        "upperLimit": "50.0",
        "lowerLimit": "0",
    },
)

HOT_WATER_TANK_USE_EXCESS_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].param.useExcessEnergy",
)

HOT_WATER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].param.excessEnergyTemp.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Set heat temp.",
        "unitId": "Temp",
        "upperLimit": "95",
        "lowerLimit": "0",
    },
)

HOT_WATER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].param.excessEnergyTemp.hyst",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Hyst. heat temp.",
        "unitId": "TempRel",
        "upperLimit": "5",
        "lowerLimit": "0",
    },
)


HOT_WATER_TANK_EXCESS_ENERGY_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].values.useExcessEnergy",
    attributes={
        "formatId": "fmtExcessEnergyInfo",
        "longText": "Excess energy HWT 1",
        "unitId": "Enum",
        "upperLimit": "2",
        "lowerLimit": "0",
    },
)

HOT_WATER_TANK_HEAT_REQUEST: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].values.heatRequestTop",
)

HOT_WATER_TANK_FRESH_WATER_FLOW: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].FreshWater.freshWaterFlow.values.actValue",
)

HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].FreshWater.freshWaterTemp.values.actValue",
    attributes={
        "formatId": "fmt3p2",
        "longText": "FWM temp.",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "0",
    },
)

HOT_WATER_TANK_TARGET_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].param.normalSetTempMax.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Temp. nom.",
        "unitId": "Temp",
        "upperLimit": "52",
        "lowerLimit": "0",
        "dynUpperLimit": 1,
    },
)

HOT_WATER_TANK_STANDBY_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].param.reducedSetTempMax.value",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Sup.temp.",
        "unitId": "Temp",
        "upperLimit": "52",
        "lowerLimit": "0",
        "dynUpperLimit": 1,
    },
)

HOT_WATER_TANK_OPERATION_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].param.operatingMode",
    attributes={
        "formatId": "fmtHotWaterTank",
        "longText": "Op.mode",
        "unitId": "Enum",
        "upperLimit": "32767",
        "lowerLimit": "0",
    },
)

HOT_WATER_TANK_CURRENT_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].topTemp.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Temp. act.",
        "unitId": "Temp",
        "upperLimit": "90",
        "lowerLimit": "20",
    },
)

HOT_WATER_TANK_CIRCULATION_RETURN_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].circTemp.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Circ. reflux temp.",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-100",
    },
)

HOT_WATER_TANK_CIRCULATION_PUMP_STATE: Final = Variable(
    name="APPL.CtrlAppl.sParam.hotWaterTank[{index}].circPump.pump.values.setValueB",
)

PASSIVE_COOLING_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.passivecooling[0].TempCoolPassive.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Temp. passive cool",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-100",
    },
)

PASSIVE_COOLING_SWITCH_VALVE_POSITION: Final = Variable(
    name="APPL.CtrlAppl.sParam.passivecooling[0].SwitchValvePassiveCool.values.actPosition",
    attributes={
        "formatId": "fmtSwitchValveState",
        "longText": "Act. Pos.",
        "unitId": "Enum",
        "upperLimit": "2",
        "lowerLimit": "0",
    },
)

PASSIVE_COOLING_CIRCULATION_PUMP_SPEED: Final = Variable(
    name="APPL.CtrlAppl.sParam.passivecooling[0].Pump.values.setValueScaled",
    attributes={
        "formatId": "fmt3p0",
        "longText": "CP speed",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "0.0",
    },
)

PASSIVE_COOLING_MIXER_TARGET_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.passivecooling[0].Mixer.values.setValue",
)

PASSIVE_COOLING_MIXER_POSITION: Final = Variable(
    name="APPL.CtrlAppl.sParam.passivecooling[0].Mixer.mixer.values.setValueScaled",
    attributes={
        "formatId": "fmt3p0",
        "longText": "Mixer nom. value",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "-1",
    },
)

PASSIVE_COOLING_MIXER_FLOW_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.passivecooling[0].Mixer.flowTemp.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Inflow temp. act.",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "0",
    },
)

PHOTOVOLTAIC_EXCESS_ENERGY_ACTIVE: Final = Variable(
    name="APPL.CtrlAppl.sParam.photovoltaics.values.excessEnergyActive",
)

PHOTOVOLTAIC_EXCESS_POWER: Final = Variable(
    name="APPL.CtrlAppl.sParam.photovoltaics.ElectricEnergyMeter.values.power",
)

PHOTOVOLTAIC_DAILY_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.photovoltaics.ElectricEnergyMeter.values.heatDay",
)

PHOTOVOLTAIC_TOTAL_ENERGY: Final = Variable(
    name="APPL.CtrlAppl.sParam.photovoltaics.ElectricEnergyMeter.values.accumulatedHeat",
)

SYSTEM_HEAT_CIRCUIT_NUMBERS: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.systemNumberOfHeatingCircuits",
    attributes={
        "formatId": "fmt2p0",
        "longText": "Qty HC",
        "upperLimit": "8",
        "lowerLimit": "0",
        "dynLowerLimit": 1,
        "dynUpperLimit": 1,
    },
)

SYSTEM_SOLAR_CIRCUIT_NUMBERS: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.systemNumberOfSolarCircuits",
    attributes={
        "dynLowerLimit": 1,
        "dynUpperLimit": 1,
        "formatId": "fmt2p0",
        "longText": "Qty solar",
        "upperLimit": "4",
        "lowerLimit": "0",
    },
)

SYSTEM_HEAT_PUMP_NUMBERS: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.systemNumberOfHeatPumps",
    attributes={
        "formatId": "fmt2p0",
        "longText": "Qty heat pumps",
        "upperLimit": "4",
        "lowerLimit": "0",
        "dynLowerLimit": 1,
        "dynUpperLimit": 1,
    },
)

SYSTEM_BUFFER_TANK_NUMBERS: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.systemNumberOfBuffers",
    attributes={
        "formatId": "fmt2p0",
        "longText": "Qty buffers",
        "upperLimit": "0",
        "lowerLimit": "0",
        "dynLowerLimit": 1,
        "dynUpperLimit": 1,
    },
)

SYSTEM_HOT_WATER_TANK_NUMBERS: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.systemNumberOfHotWaterTanks",
    attributes={
        "formatId": "fmt2p0",
        "longText": "Qty HW tank",
        "upperLimit": "4",
        "lowerLimit": "0",
        "dynLowerLimit": 1,
        "dynUpperLimit": 1,
    },
)

SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.systemNumberOfExtHeatSources",
    attributes={"formatId": "fmt2p0", "longText": "Qty ext. heat sources", "upperLimit": "1", "lowerLimit": "0"},
)

SYSTEM_SWITCH_VALVE_NUMBERS: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.systemNumberOfSwitchValves",
    attributes={
        "formatId": "fmt2p0",
        "longText": "Qty switch valves",
        "upperLimit": "0",
        "lowerLimit": "0",
        "dynLowerLimit": 1,
        "dynUpperLimit": 1,
    },
)

SYSTEM_OUTDOOR_TEMPERATURE: Final = Variable(
    name="APPL.CtrlAppl.sParam.outdoorTemp.values.actValue",
    attributes={
        "formatId": "fmtTemp",
        "longText": "Exterior temp.",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-100",
    },
)

SYSTEM_OPERATING_MODE: Final = Variable(
    name="APPL.CtrlAppl.sParam.param.operatingMode",
    attributes={
        "formatId": "fmtOperatingMode",
        "longText": "Operating mode",
        "lowerLimit": "-1",
        "unitId": "Enum",
        "upperLimit": "4",
    },
)

SYSTEM_HAS_PHOTOVOLTAICS: Final = Variable(
    name="APPL.CtrlAppl.sParam.options.hasPhotovoltaics",
)

SWITCH_VALVE_POSITION: Final = Variable(
    name="APPL.CtrlAppl.sParam.switchvalve[{index}].values.actPosition",
    attributes={
        "formatId": "fmtSwitchValveStateV1",
        "longText": "Valve pos.",
        "unitId": "Enum",
        "upperLimit": "2",
        "lowerLimit": "0",
    },
)

DEVICE_INFO_RESPONSE: Final[dict[str, int | str]] = {
    "ret": "OK",
    "revNo": 2,
    "orderNo": 000000,
    "serNo": 12345678,
    "name": "AP 440/H-A",
    "variantNo": 0,
}

SYSTEM_RESPONSE: Final[dict[str, str]] = {
    "ret": "OK",
    "name": "KeEnergy.MTec",
    "version": "2.2.2",
}

HMI_RESPONSE: Final[dict[str, str]] = {
    "ret": "OK",
    "name": "KeEnergy.WebHmi_2.2.0.0",
}

# The default block of the week timers of the fake Web HMI, 06:00 to 22:00 as seconds since midnight.
WEEK_TIMER_DAY_START_SECONDS: Final[int] = 21600
WEEK_TIMER_DAY_STOP_SECONDS: Final[int] = 79200

TIMEZONE_RESPONSE: Final[dict[str, str]] = {
    "timezone": "Europe/Vienna",
}

SYSTEM_CPU_USAGE: Final = Variable(
    name="APPL.CtrlAppl.sProcData.globalCpuTimePercent",
)

SYSTEM_WEBVIEW_CPU_USAGE: Final = Variable(
    name="APPL.CtrlAppl.sProcData.processStatus[0].cpuTimePercent",
)

SYSTEM_WEBSERVER_CPU_USAGE: Final = Variable(
    name="APPL.CtrlAppl.sProcData.processStatus[1].cpuTimePercent",
)

SYSTEM_CONTROL_CPU_USAGE: Final = Variable(
    name="APPL.CtrlAppl.sProcData.processStatus[2].cpuTimePercent",
)

SYSTEM_RAM_USAGE: Final = Variable(
    name="APPL.CtrlAppl.sProcData.RAMstatus.tmpfs",
)

SYSTEM_FREE_RAM: Final = Variable(
    name="APPL.CtrlAppl.sProcData.totFreeRAM",
)

SYSTEM_FLASH_ERASE_COUNTER: Final = Variable(
    name="APPL.CtrlAppl.sParam.values.UBIMaxEraseCounter",
)

SINGLE_DEVICE_RESPONSE: Final[Response] = [
    SYSTEM_HEAT_PUMP_NUMBERS.read("1"),
    SYSTEM_HEAT_CIRCUIT_NUMBERS.read("1"),
    SYSTEM_SOLAR_CIRCUIT_NUMBERS.read("1"),
    SYSTEM_BUFFER_TANK_NUMBERS.read("1"),
    SYSTEM_HOT_WATER_TANK_NUMBERS.read("1"),
    SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS.read("1"),
    SYSTEM_SWITCH_VALVE_NUMBERS.read("1"),
]

MULTIPLE_DEVICES_RESPONSE: Final[Response] = [
    SYSTEM_HEAT_PUMP_NUMBERS.read("1"),
    SYSTEM_HEAT_CIRCUIT_NUMBERS.read("2"),
    SYSTEM_SOLAR_CIRCUIT_NUMBERS.read("2"),
    SYSTEM_BUFFER_TANK_NUMBERS.read("2"),
    SYSTEM_HOT_WATER_TANK_NUMBERS.read("2"),
    SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS.read("2"),
    SYSTEM_SWITCH_VALVE_NUMBERS.read("2"),
]


def get_heat_pump_data(*, index: int = 0, compressor_night_speed: str = "true") -> Response:
    """Return the values of the heat pump with the index."""
    return [
        HEAT_PUMP_CONSUMING_EXCESS_ENERGY.read("true", index=index),
        HEAT_PUMP_EXCESS_ENERGY_OPERATING_TIME.read("3600", index=index),
        HEAT_PUMP_EXCESS_ENERGY_MAX_RUNTIME.read("3600", index=index),
        HEAT_PUMP_EXCESS_ENERGY_ACTIVATION_COUNTER.read("3600", index=index),
        HEAT_PUMP_CIRCULATION_PUMP_SPEED.read("0", index=index),
        HEAT_PUMP_SOURCE_PUMP_SPEED.read("0.44875106", index=index),
        HEAT_PUMP_COMPRESSOR.read("0", index=index),
        HEAT_PUMP_COMPRESSOR_NIGHT_SPEED.read("0.5", index=index),
        HEAT_PUMP_COMPRESSOR_INPUT_TEMPERATURE.read("27.200001", index=index),
        HEAT_PUMP_COMPRESSOR_OUTPUT_TEMPERATURE.read("27.200001", index=index),
        HEAT_PUMP_COMPRESSOR_USE_NIGHT_SPEED.read(compressor_night_speed, index=index),
        HEAT_PUMP_CONDENSER_TEMPERATURE.read("31.514103", index=index),
        HEAT_PUMP_VAPORIZER_TEMPERATURE.read("-4.5617409", index=index),
        HEAT_PUMP_TARGET_OVERHEATING.read("5.4999752", index=index),
        HEAT_PUMP_CURRENT_OVERHEATING.read("18.676249", index=index),
        HEAT_PUMP_EXPANSION_VALVE_POSITION.read("20", index=index),
        HEAT_PUMP_HEAT_REQUEST.read("false", index=index),
        HEAT_PUMP_HIGH_PRESSURE.read("15.61875", index=index),
        HEAT_PUMP_FLOW_TEMPERATURE.read("24.803127", index=index),
        HEAT_PUMP_LOW_PRESSURE.read("15.354687", index=index),
        HEAT_PUMP_NAME.read("WPS26", index=index),
        HEAT_PUMP_RETURN_FLOW_TEMPERATURE.read("23.904211", index=index),
        HEAT_PUMP_SOURCE_INPUT_TEMPERATURE.read("25.700001", index=index),
        HEAT_PUMP_SOURCE_OUTPUT_TEMPERATURE.read("24.896341", index=index),
        HEAT_PUMP_STATE.read("0", index=index),
        HEAT_PUMP_SUBSTATE.read("1", index=index),
        HEAT_PUMP_COMPRESSOR_POWER.read("5.5196772", index=index),
        HEAT_PUMP_HEATING_POWER.read("3.2187521", index=index),
        HEAT_PUMP_HOT_WATER_POWER.read("2.7713845", index=index),
        HEAT_PUMP_COP.read("2.5501628", index=index),
        HEAT_PUMP_HEATING_ENERGY.read("8.4317026", index=index),
        HEAT_PUMP_HEATING_ENERGY_CONSUMPTION.read("7.3290005", index=index),
        HEAT_PUMP_HEATING_SPF.read("3.3184626", index=index),
        HEAT_PUMP_COOLING_ENERGY.read("7.2140002", index=index),
        HEAT_PUMP_COOLING_ENERGY_CONSUMPTION.read("8.7180004", index=index),
        HEAT_PUMP_COOLING_SPF.read("4.2206435", index=index),
        HEAT_PUMP_HOT_WATER_ENERGY.read("7.8570004", index=index),
        HEAT_PUMP_HOT_WATER_ENERGY_CONSUMPTION.read("2.7710001", index=index),
        HEAT_PUMP_HOT_WATER_SPF.read("2.5034916", index=index),
        HEAT_PUMP_TOTAL_THERMAL_ENERGY.read("8.2230005", index=index),
        HEAT_PUMP_TOTAL_ENERGY_CONSUMPTION.read("5.2120004", index=index),
        HEAT_PUMP_TOTAL_SPF.read("2.4277346", index=index),
        HEAT_PUMP_EXCESS_ENERGY_CONSUMPTION.read("10.003001", index=index),
        HEAT_PUMP_HEATING_EXCESS_ENERGY_CONSUMPTION.read("10.003001", index=index),
        HEAT_PUMP_COOLING_EXCESS_ENERGY_CONSUMPTION.read("10.003001", index=index),
        HEAT_PUMP_HOT_WATER_EXCESS_ENERGY_CONSUMPTION.read("10.003001", index=index),
        HEAT_PUMP_OPERATING_TIME.read("3809028", index=index),
        HEAT_PUMP_MAX_RUNTIME.read("602403", index=index),
        HEAT_PUMP_ACTIVATION_COUNTER.read("477", index=index),
        HEAT_PUMP_HAS_COMPRESSOR_FAILURE.read("false", index=index),
        HEAT_PUMP_HAS_SOURCE_FAILURE.read("false", index=index),
        HEAT_PUMP_HAS_SOURCE_ACTUATOR_FAILURE.read("false", index=index),
        HEAT_PUMP_HAS_THREE_PHASE_FAILURE.read("false", index=index),
        HEAT_PUMP_HAS_SOURCE_PRESSURE_FAILURE.read("false", index=index),
        HEAT_PUMP_HAS_VFD_FAILURE.read("false", index=index),
        PASSIVE_COOLING_TEMPERATURE.read("22.299999", index=index),
        PASSIVE_COOLING_SWITCH_VALVE_POSITION.read("1", index=index),
        PASSIVE_COOLING_CIRCULATION_PUMP_SPEED.read("0.2314783", index=index),
        PASSIVE_COOLING_MIXER_FLOW_TEMPERATURE.read("24.299999", index=index),
        PASSIVE_COOLING_MIXER_TARGET_TEMPERATURE.read("19.218407", index=index),
        PASSIVE_COOLING_MIXER_POSITION.read("-1", index=index),
    ]


SINGLE_DEVICE_FIXED_DATA_RESPONSE: Final[Response] = [
    SYSTEM_HAS_PHOTOVOLTAICS.read("true"),
    HEAT_CIRCUIT_MODE.read("0"),
    HEAT_PUMP_HAS_ACTIVE_COOLING.read("false"),
    HEAT_PUMP_HAS_PASSIVE_COOLING.read("true"),
    HEAT_PUMP_ELECTRIC_ENERGY_METER_TYPE.read("2"),
    HEAT_PUMP_HEAT_METER_TYPE.read("2"),
    EXTERNAL_HEAT_SOURCE_HAS_EMISSIONS.read("false"),
]


def get_multiple_devices_fixed_data_response(
    *,
    has_passive_cooling: str = "false",
    has_cooling_circuits: bool = True,
    has_photovoltaics: str = "true",
) -> Response:
    """Return the values that are read once on setup, for a setup with several devices of each type."""
    return [
        SYSTEM_HAS_PHOTOVOLTAICS.read(has_photovoltaics),
        *HEAT_CIRCUIT_MODE.read_all("0", "1" if has_cooling_circuits else "0"),
        HEAT_PUMP_HAS_ACTIVE_COOLING.read("false"),
        HEAT_PUMP_HAS_PASSIVE_COOLING.read(has_passive_cooling),
        HEAT_PUMP_ELECTRIC_ENERGY_METER_TYPE.read("2"),
        HEAT_PUMP_HEAT_METER_TYPE.read("2"),
        *EXTERNAL_HEAT_SOURCE_HAS_EMISSIONS.read_all("true", "false"),
    ]


def get_single_device_data_response(
    heat_circuit_target_temperature_offset: str = "0",
    hot_water_tank_target_temperature: str = "51",
) -> Response:
    """Return the values of a setup with one device of each type."""
    return [
        EXTERNAL_HEAT_SOURCE_OPERATING_MODE.read("1"),
        EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE.read("23"),
        EXTERNAL_HEAT_SOURCE_HEAT_REQUEST.read("true"),
        EXTERNAL_HEAT_SOURCE_OPERATING_TIME.read("812999"),
        EXTERNAL_HEAT_SOURCE_MAX_RUNTIME.read("8129"),
        EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER.read("812"),
        EXTERNAL_HEAT_SOURCE_USE_EXCESS_ENERGY.read("true"),
        EXTERNAL_HEAT_SOURCE_MIN_RUNTIME_EXCESS_ENERGY.read("300"),
        EXTERNAL_HEAT_SOURCE_CONSUMING_EXCESS_ENERGY.read("true"),
        EXTERNAL_HEAT_SOURCE_EXCESS_ENERGY_OPERATING_TIME.read("3600"),
        EXTERNAL_HEAT_SOURCE_EXCESS_ENERGY_MAX_RUNTIME.read("3600"),
        EXTERNAL_HEAT_SOURCE_EXCESS_ENERGY_ACTIVATION_COUNTER.read("23"),
        HEAT_CIRCUIT_ROOM_TEMPERATURE.read("22.418831"),
        HEAT_CIRCUIT_ROOM_HUMIDITY.read("53"),
        HEAT_CIRCUIT_DEW_POINT.read("13.104257"),
        HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT.read("26.553419"),
        HEAT_CIRCUIT_MIXER_FLOW_TEMPERATURE.read("22.200001"),
        HEAT_CIRCUIT_MIXER_RETURN_FLOW_TEMPERATURE.read("20.200001"),
        HEAT_CIRCUIT_MIXER_POSITION.read("-1"),
        HEAT_CIRCUIT_PUMP_STATE.read("true"),
        HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE.read("21.200001"),
        HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY.read("20.5"),
        HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_DAY.read("20.5"),
        HEAT_CIRCUIT_HEATING_LIMIT_DAY.read("20"),
        HEAT_CIRCUIT_COOLING_LIMIT_DAY.read("20"),
        HEAT_CIRCUIT_EXCESS_ENERGY_HEATING_LIMIT_DAY.read("30"),
        HEAT_CIRCUIT_EXCESS_ENERGY_COOLING_LIMIT_DAY.read("10"),
        HEAT_CIRCUIT_HEAT_REQUEST.read("1"),
        HEAT_CIRCUIT_COOL_REQUEST.read("1"),
        HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY.read("18"),
        HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT.read("20"),
        HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_NIGHT.read("20"),
        HEAT_CIRCUIT_HEATING_LIMIT_NIGHT.read("18"),
        HEAT_CIRCUIT_COOLING_LIMIT_NIGHT.read("18"),
        HEAT_CIRCUIT_EXCESS_ENERGY_HEATING_LIMIT_NIGHT.read("28"),
        HEAT_CIRCUIT_EXCESS_ENERGY_COOLING_LIMIT_NIGHT.read("28"),
        HEAT_CIRCUIT_OPERATION_MODE.read("3"),
        HEAT_CIRCUIT_SELECTED_TARGET_TEMPERATURE.read("20"),
        HEAT_CIRCUIT_TARGET_TEMPERATURE.read("20.5"),
        HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET.read(heat_circuit_target_temperature_offset),
        HEAT_CIRCUIT_USE_EXCESS_ENERGY.read("true"),
        HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_TEMPERATURE.read("30"),
        HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS.read("0.69999999"),
        HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_COOLING_TEMPERATURE.read("10"),
        HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_COOLING_TEMPERATURE_HYSTERESIS.read("0.69999999"),
        HEAT_CIRCUIT_EXCESS_ENERGY_MODE.read("1"),
        HEAT_CIRCUIT_AWAY_START_DATE.read("1769036400"),
        HEAT_CIRCUIT_AWAY_END_DATE.read("1769122799"),
        HEAT_CIRCUIT_HEATING_CURVE_OFFSET.read("0.5"),
        HEAT_CIRCUIT_COOLING_CURVE_OFFSET.read("0.5"),
        HEAT_CIRCUIT_HEATING_CURVE_SLOPE.read("0.40000001"),
        HEAT_CIRCUIT_COOLING_CURVE_SLOPE.read("0.40000001"),
        HEAT_CIRCUIT_USE_HEATING_CURVE.read("false"),
        HEAT_CIRCUIT_HEATING_CURVE.read("HC4"),
        HEAT_CIRCUIT_COOLING_CURVE.read("HC2"),
        HEAT_CIRCUIT_PUMP_SPEED.read("0.5"),
        SOLAR_CIRCUIT_OPERATION_MODE.read("0"),
        SOLAR_CIRCUIT_SOURCE_TEMPERATURE.read("44.400002"),
        SOLAR_CIRCUIT_PUMP_1.read("0.62941831"),
        SOLAR_CIRCUIT_PUMP_2.read("0.43000001"),
        SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1.read("36.799999"),
        SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2.read("26.799999", index=1),
        SOLAR_CIRCUIT_TARGET_TEMPERATURE_1.read("55"),
        SOLAR_CIRCUIT_TARGET_TEMPERATURE_2.read("55", index=1),
        *SOLAR_CIRCUIT_HEAT_REQUEST.read_all("true", "false"),
        SOLAR_CIRCUIT_HEATING_ENERGY.read("1.0984564e+09"),
        SOLAR_CIRCUIT_DAILY_ENERGY.read("298018"),
        SOLAR_CIRCUIT_ACTUAL_POWER.read("3452"),
        SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2.read("true"),
        *get_heat_pump_data(compressor_night_speed="true"),
        BUFFER_TANK_CURRENT_TOP_TEMPERATURE.read("45.700001"),
        BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE.read("25.700001"),
        BUFFER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE.read("75"),
        BUFFER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS.read("2"),
        BUFFER_TANK_EXCESS_ENERGY_MODE.read("1"),
        BUFFER_TANK_OPERATING_MODE.read("0"),
        BUFFER_TANK_STANDBY_TEMPERATURE.read("10"),
        BUFFER_TANK_TARGET_TEMPERATURE.read("44"),
        BUFFER_TANK_HEAT_REQUEST.read("false"),
        BUFFER_TANK_COOL_REQUEST.read("true"),
        BUFFER_TANK_USE_EXCESS_ENERGY.read("true"),
        BUFFER_TANK_OUTDOOR_TEMPERATURE_EXCESS_ENERGY_LIMIT.read("25"),
        HOT_WATER_TANK_USE_EXCESS_ENERGY.read("true"),
        HOT_WATER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE.read("75"),
        HOT_WATER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS.read("4"),
        HOT_WATER_TANK_EXCESS_ENERGY_MODE.read("1"),
        HOT_WATER_TANK_HEAT_REQUEST.read("false"),
        HOT_WATER_TANK_FRESH_WATER_FLOW.read("true"),
        HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE.read("51"),
        HOT_WATER_TANK_TARGET_TEMPERATURE.read(hot_water_tank_target_temperature),
        HOT_WATER_TANK_STANDBY_TEMPERATURE.read("32.5"),
        HOT_WATER_TANK_OPERATION_MODE.read("3"),
        HOT_WATER_TANK_CURRENT_TEMPERATURE.read("47.700001"),
        HOT_WATER_TANK_CIRCULATION_RETURN_TEMPERATURE.read("34.5"),
        HOT_WATER_TANK_CIRCULATION_PUMP_STATE.read("false"),
        SWITCH_VALVE_POSITION.read("1"),
        PHOTOVOLTAIC_EXCESS_ENERGY_ACTIVE.read("true"),
        PHOTOVOLTAIC_EXCESS_POWER.read("437.70001"),
        PHOTOVOLTAIC_DAILY_ENERGY.read("1.5757199e+09"),
        PHOTOVOLTAIC_TOTAL_ENERGY.read("1.5757199e+09"),
        SYSTEM_OUTDOOR_TEMPERATURE.read("20.504164"),
        SYSTEM_OPERATING_MODE.read("2"),
        SYSTEM_CPU_USAGE.read("27"),
        SYSTEM_WEBVIEW_CPU_USAGE.read("34"),
        SYSTEM_WEBSERVER_CPU_USAGE.read("67"),
        SYSTEM_CONTROL_CPU_USAGE.read("7"),
        SYSTEM_RAM_USAGE.read("6432"),
        SYSTEM_FREE_RAM.read("100060"),
        SYSTEM_FLASH_ERASE_COUNTER.read("341"),
    ]


# The response of `get_single_device_data_response()` with other values.
SINGLE_DEVICE_DATA_RESPONSE: Final[Response] = replace_values(
    get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
    EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE.read("1"),
    HEAT_CIRCUIT_COOL_REQUEST.read("0"),
    HEAT_CIRCUIT_HEATING_CURVE_SLOPE.read("0.1"),
    HEAT_CIRCUIT_COOLING_CURVE_SLOPE.read("0.1"),
    HEAT_CIRCUIT_USE_HEATING_CURVE.read("true"),
    HEAT_CIRCUIT_HEATING_CURVE.read("HC1"),
    HOT_WATER_TANK_FRESH_WATER_FLOW.read("false"),
    HOT_WATER_TANK_CIRCULATION_RETURN_TEMPERATURE.read("30.5"),
)

# The values of `MULTIPLE_DEVICES_DATA_RESPONSE` are split by device type.
MULTIPLE_DEVICES_EXTERNAL_HEAT_SOURCE_DATA: Final[Response] = [
    *EXTERNAL_HEAT_SOURCE_OPERATING_MODE.read_all("0", "1"),
    *EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE.read_all("17.227032", "17.227032"),
    *EXTERNAL_HEAT_SOURCE_HEAT_REQUEST.read_all("true", "true"),
    *EXTERNAL_HEAT_SOURCE_OPERATING_TIME.read_all("812999", "812999"),
    *EXTERNAL_HEAT_SOURCE_MAX_RUNTIME.read_all("8129", "8129"),
    *EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER.read_all("812", "812"),
    *EXTERNAL_HEAT_SOURCE_USE_EXCESS_ENERGY.read_all("true", "true"),
    *EXTERNAL_HEAT_SOURCE_MIN_RUNTIME_EXCESS_ENERGY.read_all("300", "300"),
    *EXTERNAL_HEAT_SOURCE_CONSUMING_EXCESS_ENERGY.read_all("true", "true"),
    *EXTERNAL_HEAT_SOURCE_EXCESS_ENERGY_OPERATING_TIME.read_all("3600", "3600"),
    *EXTERNAL_HEAT_SOURCE_EXCESS_ENERGY_MAX_RUNTIME.read_all("3600", "3600"),
    *EXTERNAL_HEAT_SOURCE_EXCESS_ENERGY_ACTIVATION_COUNTER.read_all("23", "23"),
]

MULTIPLE_DEVICES_HEAT_CIRCUIT_DATA: Final[Response] = [
    *HEAT_CIRCUIT_ROOM_TEMPERATURE.read_all("22.418831", "22.418831"),
    *HEAT_CIRCUIT_ROOM_HUMIDITY.read_all("53", "53"),
    *HEAT_CIRCUIT_DEW_POINT.read_all("13.104257", "13.104257"),
    *HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT.read_all("26.553419", "26.553419"),
    *HEAT_CIRCUIT_MIXER_FLOW_TEMPERATURE.read_all("22.200001", "22.200001"),
    *HEAT_CIRCUIT_MIXER_RETURN_FLOW_TEMPERATURE.read_all("20.200001", "20.200001"),
    *HEAT_CIRCUIT_MIXER_POSITION.read_all("-1", "-1"),
    *HEAT_CIRCUIT_PUMP_STATE.read_all("true", "true"),
    *HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE.read_all("21.200001", "21.200001"),
    *HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY.read_all("20.5", "20.5"),
    *HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_DAY.read_all("20.5", "20.5"),
    *HEAT_CIRCUIT_HEATING_LIMIT_DAY.read_all("20", "20"),
    *HEAT_CIRCUIT_COOLING_LIMIT_DAY.read_all("20", "20"),
    *HEAT_CIRCUIT_EXCESS_ENERGY_HEATING_LIMIT_DAY.read_all("30", "30"),
    *HEAT_CIRCUIT_EXCESS_ENERGY_COOLING_LIMIT_DAY.read_all("10", "10"),
    *HEAT_CIRCUIT_HEAT_REQUEST.read_all("1", "0"),
    *HEAT_CIRCUIT_COOL_REQUEST.read_all("0", "1"),
    *HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY.read_all("18", "18"),
    *HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT.read_all("20", "20"),
    *HEAT_CIRCUIT_TARGET_COOLING_TEMPERATURE_NIGHT.read_all("20", "20"),
    *HEAT_CIRCUIT_HEATING_LIMIT_NIGHT.read_all("18", "18"),
    *HEAT_CIRCUIT_COOLING_LIMIT_NIGHT.read_all("18", "18"),
    *HEAT_CIRCUIT_EXCESS_ENERGY_HEATING_LIMIT_NIGHT.read_all("28", "28"),
    *HEAT_CIRCUIT_EXCESS_ENERGY_COOLING_LIMIT_NIGHT.read_all("28", "28"),
    *HEAT_CIRCUIT_OPERATION_MODE.read_all("2", "1"),
    *HEAT_CIRCUIT_SELECTED_TARGET_TEMPERATURE.read_all("20", "20"),
    *HEAT_CIRCUIT_TARGET_TEMPERATURE.read_all("20.5", "20.5"),
    *HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET.read_all("1.5", "0"),
    *HEAT_CIRCUIT_USE_EXCESS_ENERGY.read_all("true", "false"),
    *HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_TEMPERATURE.read_all("30", "30"),
    *HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS.read_all("0.69999999", "0.69999999"),
    *HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_COOLING_TEMPERATURE.read_all("10", "10"),
    *HEAT_CIRCUIT_EXCESS_ENERGY_TARGET_COOLING_TEMPERATURE_HYSTERESIS.read_all("0.69999999", "0.69999999"),
    *HEAT_CIRCUIT_EXCESS_ENERGY_MODE.read_all("1", "0"),
    *HEAT_CIRCUIT_AWAY_START_DATE.read_all("1769036400", "1769036400"),
    *HEAT_CIRCUIT_AWAY_END_DATE.read_all("1769122799", "1769122799"),
    *HEAT_CIRCUIT_HEATING_CURVE_OFFSET.read_all("1.5", "-1.5"),
    *HEAT_CIRCUIT_COOLING_CURVE_OFFSET.read_all("0.5", "-1.5"),
    *HEAT_CIRCUIT_HEATING_CURVE_SLOPE.read_all("0.5", "0.60000002"),
    *HEAT_CIRCUIT_COOLING_CURVE_SLOPE.read_all("0.5", "0.60000002"),
    *HEAT_CIRCUIT_USE_HEATING_CURVE.read_all("false", "true"),
    *HEAT_CIRCUIT_HEATING_CURVE.read_all("HC6", "HC7"),
    *HEAT_CIRCUIT_COOLING_CURVE.read_all("HC5", "HC5"),
    *HEAT_CIRCUIT_PUMP_SPEED.read_all("0.5", "0.5"),
]

MULTIPLE_DEVICES_SOLAR_CIRCUIT_DATA: Final[Response] = [
    *SOLAR_CIRCUIT_OPERATION_MODE.read_all("0", "1"),
    *SOLAR_CIRCUIT_SOURCE_TEMPERATURE.read_all("44.400002", "34.400002"),
    *SOLAR_CIRCUIT_PUMP_1.read_all("0.62941831", "0.43000001"),
    *SOLAR_CIRCUIT_PUMP_2.read_all("0.73000002", "0.52999997"),
    SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1.read("36.799999"),
    SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2.read("26.799999", index=1),
    SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1.read("46.799999", index=2),
    SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2.read("56.799999", index=3),
    SOLAR_CIRCUIT_TARGET_TEMPERATURE_1.read("55"),
    SOLAR_CIRCUIT_TARGET_TEMPERATURE_2.read("54", index=1),
    SOLAR_CIRCUIT_TARGET_TEMPERATURE_1.read("53", index=2),
    SOLAR_CIRCUIT_TARGET_TEMPERATURE_2.read("52", index=3),
    *SOLAR_CIRCUIT_HEAT_REQUEST.read_all("true", "false"),
    SOLAR_CIRCUIT_HEAT_REQUEST.read("false", index=2),
    SOLAR_CIRCUIT_HEAT_REQUEST.read("true", index=3),
    *SOLAR_CIRCUIT_HEATING_ENERGY.read_all("1.0984564e+09", "1.0984564e+09"),
    *SOLAR_CIRCUIT_DAILY_ENERGY.read_all("298018", "298018"),
    *SOLAR_CIRCUIT_ACTUAL_POWER.read_all("3452", "2452"),
    *SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2.read_all("false", "true"),
]

# The heat pump, buffer and hot water tanks, switch valves, photovoltaics and system, the device types after the solar
# circuits.
MULTIPLE_DEVICES_HEAT_PUMP_TO_SYSTEM_DATA: Final[Response] = [
    *get_heat_pump_data(compressor_night_speed="true"),
    *BUFFER_TANK_CURRENT_TOP_TEMPERATURE.read_all("45.700001", "35.700001"),
    *BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE.read_all("15.695418", "25.700001"),
    *BUFFER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE.read_all("75", "75"),
    *BUFFER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS.read_all("2", "2"),
    *BUFFER_TANK_EXCESS_ENERGY_MODE.read_all("1", "0"),
    *BUFFER_TANK_OPERATING_MODE.read_all("0", "1"),
    *BUFFER_TANK_STANDBY_TEMPERATURE.read_all("10", "11"),
    *BUFFER_TANK_TARGET_TEMPERATURE.read_all("44", "43"),
    *BUFFER_TANK_HEAT_REQUEST.read_all("false", "true"),
    *BUFFER_TANK_COOL_REQUEST.read_all("true", "false"),
    *BUFFER_TANK_USE_EXCESS_ENERGY.read_all("true", "false"),
    *BUFFER_TANK_OUTDOOR_TEMPERATURE_EXCESS_ENERGY_LIMIT.read_all("25", "25"),
    *HOT_WATER_TANK_USE_EXCESS_ENERGY.read_all("true", "false"),
    *HOT_WATER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE.read_all("75", "75"),
    *HOT_WATER_TANK_EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS.read_all("4", "4"),
    *HOT_WATER_TANK_EXCESS_ENERGY_MODE.read_all("1", "0"),
    *HOT_WATER_TANK_HEAT_REQUEST.read_all("false", "true"),
    *HOT_WATER_TANK_FRESH_WATER_FLOW.read_all("false", "true"),
    *HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE.read_all("51.200001", "51.200001"),
    *HOT_WATER_TANK_TARGET_TEMPERATURE.read_all("51", "51"),
    *HOT_WATER_TANK_STANDBY_TEMPERATURE.read_all("32.5", "32.5"),
    *HOT_WATER_TANK_OPERATION_MODE.read_all("3", "0"),
    *HOT_WATER_TANK_CURRENT_TEMPERATURE.read_all("47.700001", "47.700001"),
    *HOT_WATER_TANK_CIRCULATION_RETURN_TEMPERATURE.read_all("30.5", "27.5"),
    *HOT_WATER_TANK_CIRCULATION_PUMP_STATE.read_all("true", "false"),
    *SWITCH_VALVE_POSITION.read_all("0", "1"),
    PHOTOVOLTAIC_EXCESS_ENERGY_ACTIVE.read("true"),
    PHOTOVOLTAIC_EXCESS_POWER.read("437.70001"),
    PHOTOVOLTAIC_DAILY_ENERGY.read("1.5757199e+09"),
    PHOTOVOLTAIC_TOTAL_ENERGY.read("1.5757199e+09"),
    SYSTEM_OUTDOOR_TEMPERATURE.read("20.504164"),
    SYSTEM_OPERATING_MODE.read("2"),
    SYSTEM_CPU_USAGE.read("27"),
    SYSTEM_WEBVIEW_CPU_USAGE.read("34"),
    SYSTEM_WEBSERVER_CPU_USAGE.read("67"),
    SYSTEM_CONTROL_CPU_USAGE.read("7"),
    SYSTEM_RAM_USAGE.read("6432"),
    SYSTEM_FREE_RAM.read("100060"),
    SYSTEM_FLASH_ERASE_COUNTER.read("341"),
]

MULTIPLE_DEVICES_DATA_RESPONSE: Final[Response] = [
    *MULTIPLE_DEVICES_EXTERNAL_HEAT_SOURCE_DATA,
    *MULTIPLE_DEVICES_HEAT_CIRCUIT_DATA,
    *MULTIPLE_DEVICES_SOLAR_CIRCUIT_DATA,
    *MULTIPLE_DEVICES_HEAT_PUMP_TO_SYSTEM_DATA,
]

# The `MULTIPLE_DEVICES_DATA_RESPONSE` with other modes and settings.
MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE: Final[Response] = replace_values(
    MULTIPLE_DEVICES_DATA_RESPONSE,
    EXTERNAL_HEAT_SOURCE_USE_EXCESS_ENERGY.read("false", index=1),
    *HEAT_CIRCUIT_OPERATION_MODE.read_all("4", "4"),
    *HEAT_CIRCUIT_HEATING_CURVE_OFFSET.read_all("4.5", "-4.5"),
    *HEAT_CIRCUIT_COOLING_CURVE_OFFSET.read_all("4.5", "-4.5"),
    *HEAT_CIRCUIT_HEATING_CURVE_SLOPE.read_all("0.69999999", "0.80000001"),
    *HEAT_CIRCUIT_COOLING_CURVE_SLOPE.read_all("0.69999999", "0.80000001"),
    *HEAT_CIRCUIT_HEATING_CURVE.read_all("HC FBH", "HC HK"),
    *HEAT_CIRCUIT_COOLING_CURVE.read_all("HC2", "HC2"),
    *SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2.read_all("true", "false"),
    HEAT_PUMP_COMPRESSOR_USE_NIGHT_SPEED.read("false"),
    *BUFFER_TANK_OPERATING_MODE.read_all("1", "2"),
    *HOT_WATER_TANK_OPERATION_MODE.read_all("2", "1"),
    HOT_WATER_TANK_CIRCULATION_RETURN_TEMPERATURE.read("36.5", index=1),
    *HOT_WATER_TANK_CIRCULATION_PUMP_STATE.read_all("false", "true"),
)


# The `MULTIPLE_DEVICES_DATA_RESPONSE` after an update of the entities.
ENTITY_UPDATED_DATA_RESPONSE: Final[Response] = replace_values(
    MULTIPLE_DEVICES_DATA_RESPONSE,
    *EXTERNAL_HEAT_SOURCE_OPERATING_MODE.read_all("1", "0"),
    *EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE.read_all("13", "12"),
    EXTERNAL_HEAT_SOURCE_USE_EXCESS_ENERGY.read("false", index=1),
    HEAT_CIRCUIT_OPERATION_MODE.read("3"),
    *HEAT_CIRCUIT_HEATING_CURVE_OFFSET.read_all("0.5", "-0.5"),
    HEAT_CIRCUIT_COOLING_CURVE_OFFSET.read("-0.5", index=1),
    *HEAT_CIRCUIT_HEATING_CURVE_SLOPE.read_all("0.2", "0.30000001"),
    *HEAT_CIRCUIT_COOLING_CURVE_SLOPE.read_all("0.2", "0.30000001"),
    *HEAT_CIRCUIT_USE_HEATING_CURVE.read_all("true", "false"),
    *HEAT_CIRCUIT_HEATING_CURVE.read_all("HC2", "HC3"),
    *HEAT_CIRCUIT_COOLING_CURVE.read_all("HC4", "HC4"),
    SOLAR_CIRCUIT_PUMP_1.read("0.67000002", index=1),
    SOLAR_CIRCUIT_PUMP_2.read("0.43000001"),
    SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1.read("36.799999", index=2),
    SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2.read("26.799999", index=3),
    SOLAR_CIRCUIT_TARGET_TEMPERATURE_2.read("55", index=1),
    SOLAR_CIRCUIT_TARGET_TEMPERATURE_1.read("55", index=2),
    SOLAR_CIRCUIT_TARGET_TEMPERATURE_2.read("55", index=3),
    SOLAR_CIRCUIT_HEAT_REQUEST.read("true", index=2),
    SOLAR_CIRCUIT_HEAT_REQUEST.read("false", index=3),
    SOLAR_CIRCUIT_ACTUAL_POWER.read("3452", index=1),
    *SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2.read_all("true", "false"),
    *BUFFER_TANK_CURRENT_TOP_TEMPERATURE.read_all("47.700001", "37.700001"),
    *BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE.read_all("25.700001", "15.695418"),
    HOT_WATER_TANK_EXCESS_ENERGY_MODE.read("2", index=1),
    HOT_WATER_TANK_CIRCULATION_RETURN_TEMPERATURE.read("32.5", index=1),
    *HOT_WATER_TANK_CIRCULATION_PUMP_STATE.read_all("false", "true"),
    *SWITCH_VALVE_POSITION.read_all("1", "0"),
)


# The `MULTIPLE_DEVICES_DATA_RESPONSE` without the solar circuits and with other values.
MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE: Final[Response] = replace_values(
    [
        *MULTIPLE_DEVICES_EXTERNAL_HEAT_SOURCE_DATA,
        *MULTIPLE_DEVICES_HEAT_CIRCUIT_DATA,
        *MULTIPLE_DEVICES_HEAT_PUMP_TO_SYSTEM_DATA,
    ],
    EXTERNAL_HEAT_SOURCE_USE_EXCESS_ENERGY.read("false", index=1),
    HEAT_CIRCUIT_OPERATION_MODE.read("0", index=1),
    HEAT_CIRCUIT_COOLING_CURVE_OFFSET.read("1.5"),
    *HEAT_CIRCUIT_COOLING_CURVE.read_all("HC2", "HC2"),
)

# The `MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE` without the heating circuits, which are skipped by
# their multiplier.
MULTIPLE_DEVICES_WITHOUT_SOLAR_AND_HEATING_CIRCUITS_DATA_RESPONSE: Final[Response] = replace_values(
    [
        *MULTIPLE_DEVICES_EXTERNAL_HEAT_SOURCE_DATA,
        *MULTIPLE_DEVICES_HEAT_PUMP_TO_SYSTEM_DATA,
    ],
    EXTERNAL_HEAT_SOURCE_USE_EXCESS_ENERGY.read("false", index=1),
    BUFFER_TANK_TARGET_TEMPERATURE.read("42"),
)


def get_single_device_responses(*responses: ReadResponse) -> list[ReadResponse]:
    """Return the responses of a setup with one device of each type, followed by the responses of the updates."""
    return [SINGLE_DEVICE_RESPONSE, SINGLE_DEVICE_FIXED_DATA_RESPONSE, *responses]


def get_multiple_devices_responses(
    *responses: ReadResponse,
    has_passive_cooling: str = "false",
    has_cooling_circuits: bool = True,
    has_photovoltaics: str = "true",
) -> list[ReadResponse]:
    """Return the responses of a setup with several devices of each type, followed by the responses of the updates."""
    return [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(
            has_passive_cooling=has_passive_cooling,
            has_cooling_circuits=has_cooling_circuits,
            has_photovoltaics=has_photovoltaics,
        ),
        *responses,
    ]


CURVE_POOL: Final[tuple[str, ...]] = (
    "HC1",
    "HC2",
    "HC3",
    "HC4",
    "HC5",
    "HC6",
    "HC7",
    "HC8",
    "ValveOffset",
    "VFS5-100",
    "Fan",
    "PowerLimit",
    "HC FBH",
    "HC HK",
    "ValveOffsetAT",
    "Fan WPLK412",
    *("",) * 14,
)

CURVE_NAMES_RESPONSE: Final[Response] = [
    {
        "name": f"APPL.CtrlAppl.sParam.linTabPool[{index}].name",
        "value": name,
    }
    for index, name in enumerate(CURVE_POOL)
]


def get_curve_points_response(
    *,
    renamed: dict[str, str] | None = None,
    points: tuple[tuple[str, str], ...] | None = None,
) -> Response:
    """Return the name, the number of points and the 16 points of each curve (`HC...`) of the pool.

    Every curve has 7 points from -15 °C outdoor to 20 °C flow temperature. `renamed` changes the name of a curve
    in the points, e.g. to a name that does not match the names of `CURVE_NAMES_RESPONSE`.
    `points` replaces the (outdoor, flow) points and their number of every curve.
    """
    curve_points: tuple[tuple[str, str], ...] = points or (("-15", "20"),) * 7
    point_attributes: Attributes = {"formatId": "fmtCurrent", "upperLimit": "90000", "lowerLimit": "-90000"}
    response: Response = []

    for index, name in enumerate(CURVE_POOL):
        if not name.startswith("HC"):
            continue

        prefix: str = f"APPL.CtrlAppl.sParam.linTabPool[{index}]"
        response += [
            {
                "name": f"{prefix}.name",
                "value": (renamed or {}).get(name, name),
            },
            {
                "name": f"{prefix}.noOfPoints",
                "attributes": {"formatId": "fmt2p0", "longText": "QTY points", "upperLimit": "16", "lowerLimit": "0"},
                "value": str(len(curve_points)),
            },
        ]

        for point in range(16):
            outdoor, flow = curve_points[point] if point < len(curve_points) else ("-15", "20")
            response += [
                {
                    "name": f"{prefix}.points[{point}].x",
                    "attributes": {**point_attributes, "longText": "Point X"},
                    "value": outdoor,
                },
                {
                    "name": f"{prefix}.points[{point}].y",
                    "attributes": {**point_attributes, "longText": "Point Y"},
                    "value": flow,
                },
            ]

    return response


CURVES_RESPONSE: Final[list[Response]] = [
    CURVE_NAMES_RESPONSE,
    get_curve_points_response(),
]

# The curve HC1 was renamed on the control unit after the setup.
CURVES_RENAMED_RESPONSE: Final[list[Response]] = [
    [{**value, "value": "INVALID"} if value["value"] == "HC1" else value for value in CURVE_NAMES_RESPONSE],
    get_curve_points_response(renamed={"HC1": "INVALID"}),
]

# The control unit has no curves, so the curves in use (e.g. `HC6`) do not exist.
CURVES_WITHOUT_NAMES_RESPONSE: Final[list[Response]] = [
    [{**value, "value": ""} for value in CURVE_NAMES_RESPONSE],
    get_curve_points_response(),
]
