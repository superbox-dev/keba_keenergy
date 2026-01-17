import json
from typing import Any

FILTER_REQUESTS: dict[str, Any] = {"ret": "OK", "children": []}


EXTERNAL_HEAT_SOURCE_OPERATING_MODE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.extHeatSource[%s].param.operatingMode",
        "attributes": {
            "formatId": "fmtExternalSourceType",
            "longText": "Oper. mode",
            "unitId": "Enum",
            "upperLimit": "2",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.extHeatSource[%s].values.setTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. nom.",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "20"
        },
        "value": "%s"
    }
"""

EXTERNAL_HEAT_SOURCE_HEAT_REQUEST: str = """
    {
        "name": "APPL.CtrlAppl.sParam.extHeatSource[%s].DO.values.setValueB",
        "attributes": {
            "longText": "Dig. request"
        },
        "value": "%s"
    }
"""

EXTERNAL_HEAT_SOURCE_OPERATING_TIME: str = """
    {
        "name": "APPL.CtrlAppl.sParam.extHeatSource[%s].DO.operationalData.operationalTimeS",
        "attributes": {
            "formatId": "fmt6p0",
            "longText": "Operational hrs.",
            "unitId": "TimeHour"
        },
        "value": "%s"
    }
"""

EXTERNAL_HEAT_SOURCE_MAX_RUNTIME: str = """
    {
        "name": "APPL.CtrlAppl.sParam.extHeatSource[%s].DO.operationalData.maxRunTimeS",
        "attributes": {
            "formatId": "fmt6p1",
            "longText": "Max run-time",
            "unitId": "TimeHour"
        },
        "value": "%s"
    }
"""

EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER: str = """
    {
        "name": "APPL.CtrlAppl.sParam.extHeatSource[%s].DO.operationalData.activationCounter",
        "attributes": {
            "formatId": "fmt6p0",
            "longText": "Turn-on cycles"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_HAS_ROOM_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.heatCircuit[%s].hasRoomTemp",
        "attributes": {
            "longText": "With room temp. sensor"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_HAS_ROOM_HUMIDITY: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.heatCircuit[%s].hasRoomHumidity",
        "attributes": {
            "longText": "With room humidity sensor"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_ROOM_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].tempRoom.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. act.",
            "unitId": "Temp",
            "upperLimit": "80",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_ROOM_HUMIDITY: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].humidityRoom.values.actValue",
        "attributes": {
            "formatId": "fmt3p0",
            "longText": "Room humidity act.",
            "unitId": "Pct",
            "upperLimit": "100",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_DEW_POINT: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].dewPoint.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Dew Point",
            "unitId": "Temp",
            "upperLimit": "50.0",
            "lowerLimit": "-20.0"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].values.flowSetTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Nominal temp.",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_FLOW_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].values.flowSetTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Nominal temp.",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].heatCircuitMixer.flowTemp.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Inflow temp. act.",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].param.normalSetTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. Day",
            "unitId": "Temp",
            "upperLimit": "30",
            "lowerLimit": "10"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_HEATING_LIMIT_DAY: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].param.thresholdDayTemp.value",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Heating limit Day",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "-20"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_HEAT_REQUEST: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].values.heatRequest",
        "attributes": {
            "formatId": "fmtReqInfo",
            "longText": "Heat request",
            "unitId": "Enum",
            "upperLimit": "6",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].param.holidaySetTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. Vacation",
            "unitId": "Temp",
            "upperLimit": "30",
            "lowerLimit": "10"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].param.reducedSetTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. night",
            "unitId": "Temp",
            "upperLimit": "30",
            "lowerLimit": "10"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_HEATING_LIMIT_NIGHT: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].param.thresholdNightTemp.value",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Heat limit Night",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "-20"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_OPERATION_MODE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].param.operatingMode",
        "attributes": {
            "formatId": "fmtHcMode",
            "longText": "Operating mode",
            "unitId": "Enum",
            "upperLimit": "32767",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_TARGET_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].values.setValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. Nom.",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "10"
        },
        "value": "%s"
    }
"""

HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].param.offsetRoomTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. Offset",
            "unitId": "TempRel",
            "upperLimit": "2.5",
            "lowerLimit": "-2.5"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_OPERATION_MODE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.solarCircuit[%s].param.operatingMode",
        "attributes": {
            "formatId": "fmtSolarOpMode",
            "longText": "Oper. mode",
            "unitId": "Enum",
            "upperLimit": "32767",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_SOURCE_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.solarCircuit[%s].collectorTemp.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Source temp.",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "20"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_PUMP_1: str = """
    {
        "name": "APPL.CtrlAppl.sParam.solarCircuit[%s].values.pump1",
        "attributes": {
            "formatId": "fmt3p0",
            "longText": "Pump 1",
            "unitId": "Pct100",
            "upperLimit": "1",
            "lowerLimit": "0.0"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_PUMP_2: str = """
    {
        "name": "APPL.CtrlAppl.sParam.solarCircuit[%s].values.pump2",
        "attributes": {
            "formatId": "fmt3p0",
            "longText": "Pump 2",
            "unitId": "Pct100",
            "upperLimit": "1",
            "lowerLimit": "0.0"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1: str = """
    {
        "name": "APPL.CtrlAppl.sParam.genericHeat[%s].referenceTemp.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. act.1",
            "unitId": "Temp"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2: str = """
    {
        "name": "APPL.CtrlAppl.sParam.genericHeat[%s].referenceTemp.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. act.2",
            "unitId": "Temp"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_TARGET_TEMPERATURE_1: str = """
    {
        "name": "APPL.CtrlAppl.sParam.genericHeat[%s].param.setTempMax.value",
         "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. nom. 1",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_TARGET_TEMPERATURE_2: str = """
    {
        "name": "APPL.CtrlAppl.sParam.genericHeat[%s].param.setTempMax.value",
         "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. nom. 2",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_HEAT_REQUEST: str = """
    {
        "name": "APPL.CtrlAppl.sParam.genericHeat[%s].values.heatRequest",
        "attributes": {
            "unitId": "Enum",
            "upperLimit": "6",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_HEATING_ENERGY: str = """
    {
        "name": "APPL.CtrlAppl.sParam.solarCircuit[%s].heatMeter.values.accumulatedHeat",
        "attributes": {
            "formatId": "fmt6p0",
            "longText": "Heat quantity",
            "unitId": "kWh",
            "upperLimit": "900000",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_DAILY_ENERGY: str = """
    {
        "name": "APPL.CtrlAppl.sParam.solarCircuit[%s].heatMeter.values.heatDay",
        "attributes": {
            "formatId": "fmt6p1",
            "longText": "Energy per day",
            "unitId": "kWh"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_ACTUAL_POWER: str = """
    {
        "name": "APPL.CtrlAppl.sParam.solarCircuit[%s].heatMeter.values.power",
        "attributes": {
            "formatId": "fmt6p0",
            "longText": "Act. power",
            "unitId": "Pwr"
        },
        "value": "%s"
    }
"""

SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2: str = """
    {
       "name": "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[%s]",
        "attributes": {
            "longText": "Priority 1 bef. 2"
        },
        "value": "%s"
    }
"""

HEAT_PUMP_CIRCULATION_PUMP: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].CircPump.values.setValueScaled",
    "attributes": {
        "formatId": "fmt3p0",
        "longText": "Circulation pump",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "0.0",
    },
    "value": "0",
}

HEAT_PUMP_SOURCE_PUMP_SPEED: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].Source.values.setValueScaled",
    "attributes": {
        "formatId": "fmt3p0",
        "longText": "Source",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "0.0",
    },
    "value": "0.44875106",
}

HEAT_PUMP_COMPRESSOR: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].Compressor.values.setValueScaled",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Compressor",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "0.0",
    },
    "value": "0",
}

HEAT_PUMP_COMPRESSOR_NIGHT_SPEED: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.maxPowerScaledNight",
    "attributes": {
        "formatId": "fmt3p0",
        "longText": "Max. pwr. limit night",
        "unitId": "Pct100",
        "upperLimit": "1",
        "lowerLimit": "0.5",
    },
    "value": "0.5",
}

HEAT_PUMP_COMPRESSOR_INPUT_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempCompressorIn.values.actValue",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Comp. in temp.",
        "unitId": "Temp",
    },
    "value": "27.200001",
}

HEAT_PUMP_COMPRESSOR_OUTPUT_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempCompressorOut.values.actValue",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Comp. out temp.",
        "unitId": "Temp",
    },
    "value": "27.200001",
}

HEAT_PUMP_COMPRESSOR_USE_NIGHT_SPEED: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed",
    "attributes": {
        "longText": "Day/Night switch",
    },
    "value": "true",
}

HEAT_PUMP_CONDENSER_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].OverHeatCtrl.values.tempCond",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Cond. temp.",
        "unitId": "Temp",
        "upperLimit": "200",
        "lowerLimit": "0",
    },
    "value": "31.514103",
}

HEAT_PUMP_VAPORIZER_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].OverHeatCtrl.values.tempVap",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Evap. temp.",
        "unitId": "Temp",
    },
    "value": "-4.5617409",
}

HEAT_PUMP_HEAT_REQUEST: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].values.request",
    "attributes": {
        "longText": "Heat pump request",
    },
    "value": "false",
}

HEAT_PUMP_HIGH_PRESSURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].HighPressure.values.actValue",
    "attributes": {
        "formatId": "fmt3p2",
        "longText": "High pressure",
        "unitId": "PressBar",
    },
    "value": "15.61875",
}

HEAT_PUMP_LOW_PRESSURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].LowPressure.values.actValue",
    "attributes": {
        "formatId": "fmt3p2",
        "longText": "Low pressure",
        "unitId": "PressBar",
    },
    "value": "15.354687",
}

HEAT_PUMP_FLOW_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempHeatFlow.values.actValue",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Inflow temp.",
        "unitId": "Temp",
    },
    "value": "24.800001",
}

HEAT_PUMP_RETURN_FLOW_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempHeatReflux.values.actValue",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Reflux temp.",
        "unitId": "Temp",
    },
    "value": "23.9",
}

HEAT_PUMP_NAME: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].param.name",
    "attributes": {"longText": "Name"},
    "value": "WPS26",
}

HEAT_PUMP_SOURCE_INPUT_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempSourceIn.values.actValue",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Source in temp.",
        "unitId": "Temp",
    },
    "value": "25.700001",
}

HEAT_PUMP_SOURCE_OUTPUT_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempSourceOut.values.actValue",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Source out temp.",
        "unitId": "Temp",
    },
    "value": "24.9",
}

HEAT_PUMP_STATE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState",
    "attributes": {
        "formatId": "fmtHPState",
        "longText": "State",
        "unitId": "Enum",
        "upperLimit": "32767",
        "lowerLimit": "0",
    },
    "value": "0",
}

HEAT_PUMP_SUBSTATE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpSubState",
    "attributes": {
        "formatId": "fmtHPSubState",
        "longText": "Substate",
        "unitId": "Enum",
        "upperLimit": "32767",
        "lowerLimit": "0",
    },
    "value": "1",
}

HEAT_PUMP_COMPRESSOR_POWER: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].ElectricEnergyMeter.values.power",
    "attributes": {
        "formatId": "fmt3p2",
        "longText": "Power input",
        "unitId": "Pwr",
    },
    "value": "5.52",
}

HEAT_PUMP_HEATING_POWER: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].HeatMeter.values.power",
    "attributes": {
        "formatId": "fmt3p2",
        "longText": "Heating power",
        "unitId": "Pwr",
    },
    "value": "3.22",
}

HEAT_PUMP_HOT_WATER_POWER: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].HotWaterMeter.values.power",
    "attributes": {
        "formatId": "fmt3p2",
        "longText": "Hot water power",
        "unitId": "Pwr",
    },
    "value": "2.77",
}

HEAT_PUMP_COP: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].values.COP",
    "attributes": {
        "formatId": "fmt3p2",
        "longText": "COP",
    },
    "value": "2.55",
}

HEAT_PUMP_HEATING_ENERGY: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.heating.energy",
    "attributes": {
        "formatId": "fmt4p0",
        "longText": "Heating energy",
        "unitId": "kWhwithoutConv",
    },
    "value": "8.43",
}

HEAT_PUMP_HEATING_ENERGY_CONSUMPTION: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.heating.electricalenergy",
    "attributes": {
        "formatId": "fmt4p0",
        "longText": "Heat el. energy",
        "unitId": "kWhwithoutConv",
    },
    "value": "7.33",
}

HEAT_PUMP_HEATING_SPF: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].EnergyEfficiencyRatioHeat",
    "attributes": {
        "longText": "SPF heating",
    },
    "value": "3.32",
}

HEAT_PUMP_COOLING_ENERGY: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.cooling.energy",
    "attributes": {
        "formatId": "fmt4p0",
        "longText": "Cooling energy",
        "unitId": "kWhwithoutConv",
    },
    "value": "7.21",
}

HEAT_PUMP_COOLING_ENERGY_CONSUMPTION: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.cooling.electricalenergy",
    "attributes": {
        "formatId": "fmt4p0",
        "longText": "Cool el. energy",
        "unitId": "kWhwithoutConv",
    },
    "value": "8.72",
}

HEAT_PUMP_COOLING_SPF: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].EnergyEfficiencyRatioCool",
    "attributes": {
        "formatId": "fmt3p2",
        "longText": "SPF cooling",
    },
    "value": "4.22",
}

HEAT_PUMP_HOT_WATER_ENERGY: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.domHotWater.energy",
    "attributes": {
        "formatId": "fmt4p0",
        "longText": "Dom. HW energy",
        "unitId": "kWhwithoutConv",
    },
    "value": "7.86",
}

HEAT_PUMP_HOT_WATER_ENERGY_CONSUMPTION: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.domHotWater.electricalenergy",
    "attributes": {
        "formatId": "fmt4p0",
        "longText": "Dom.HW el. energy",
        "unitId": "kWhwithoutConv",
    },
    "value": "2.77",
}

HEAT_PUMP_HOT_WATER_SPF: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].EnergyEfficiencyRatioDomHotWater",
    "attributes": {
        "longText": "SPF DHW",
    },
    "value": "2.50",
}

HEAT_PUMP_TOTAL_THERMAL_ENERGY: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.energy",
    "attributes": {
        "formatId": "fmt4p0",
        "longText": "Energy",
        "unitId": "kWhwithoutConv",
    },
    "value": "8.22",
}

HEAT_PUMP_TOTAL_ENERGY_CONSUMPTION: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.electricalenergy",
    "attributes": {
        "formatId": "fmt4p0",
        "longText": "El. energy",
        "unitId": "kWhwithoutConv",
    },
    "value": "5.21",
}

HEAT_PUMP_TOTAL_SPF: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sStatisticalData.heatpump[0].EnergyEfficiencyRatio",
    "attributes": {
        "formatId": "fmt3p2",
        "longText": "SPF general",
    },
    "value": "2.43",
}


HEAT_PUMP_OPERATING_TIME: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].operationalData.operationalTimeS",
    "attributes": {
        "formatId": "fmt6p0",
        "longText": "Operational hrs.",
        "unitId": "TimeHour",
    },
    "value": "3809028",
}


HEAT_PUMP_MAX_RUNTIME: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].operationalData.maxRunTimeS",
    "attributes": {
        "formatId": "fmt6p1",
        "longText": "Max run-time",
        "unitId": "TimeHour",
    },
    "value": "602403",
}


HEAT_PUMP_ACTIVATION_COUNTER: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].operationalData.activationCounter",
    "attributes": {
        "formatId": "fmt6p0",
        "longText": "Turn-on cycles",
    },
    "value": "477",
}


HEAT_PUMP_HAS_PASSIVE_COOLING: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.heatpump[0].hasPassiveCooling",
        "attributes": {
            "longText": "With passive cooling"
        },
        "value": "%s"
    }
"""

BUFFER_TANK_CURRENT_TOP_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.bufferTank[%s].topTemp.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. top act.",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "5"
        },
        "value": "%s"
    }
"""

BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.bufferTank[%s].midTemp.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. bottom act.",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "5"
        },
        "value": "%s"
    }
"""

BUFFER_TANK_OPERATING_MODE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.bufferTank[%s].param.operatingMode",
        "attributes": {
            "formatId": "fmtBufferMode",
            "longText": "Oper. mode",
            "unitId": "Enum",
            "upperLimit": "32767",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

BUFFER_TANK_STANDBY_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.bufferTank[%s].param.backupTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Backup temp.",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

BUFFER_TANK_TARGET_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.bufferTank[%s].values.setTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Set temp.",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

BUFFER_TANK_HEAT_REQUEST: str = """
    {
        "name": "APPL.CtrlAppl.sParam.bufferTank[%s].values.heatRequestTop",
        "attributes": {},
        "value": "%s"
    }
"""

BUFFER_TANK_COOL_REQUEST: str = """
    {
        "name": "APPL.CtrlAppl.sParam.bufferTank[%s].values.coolRequestBot",
        "attributes": {},
        "value": "%s"
    }
"""

HOT_WATER_TANK_HEAT_REQUEST: str = """
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[%s].values.heatRequestTop",
        "attributes": {
            "longText": "Heat requirement"
        },
        "value": "%s"
    }
"""

HOT_WATER_TANK_HOT_WATER_FLOW: str = """
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[%s].FreshWater.freshWaterFlow.values.actValue",
        "attributes": {
            "longText": "FWM flow switch"
        },
        "value": "%s"
    }
"""

HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[%s].FreshWater.freshWaterTemp.values.actValue",
        "attributes": {
            "formatId": "fmt3p2",
            "longText": "FWM temp.",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

HOT_WATER_TANK_TARGET_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[%s].param.normalSetTempMax.value",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. nom.",
            "unitId": "Temp",
            "upperLimit": "52",
            "lowerLimit": "0",
            "dynUpperLimit": 1
        },
        "value": "%s"
    }
"""

HOT_WATER_TANK_STANDBY_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[%s].param.reducedSetTempMax.value",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Sup.temp.",
            "unitId": "Temp",
            "upperLimit": "52",
            "lowerLimit": "0",
            "dynUpperLimit": 1
        },
        "value": "%s"
    }
"""

HOT_WATER_TANK_OPERATION_MODE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[%s].param.operatingMode",
        "attributes": {
            "formatId": "fmtHotWaterTank",
            "longText": "Op.mode",
            "unitId": "Enum",
            "upperLimit": "32767",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

HOT_WATER_CURRENT_TEMPERATURE: str = """
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[%s].topTemp.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. act.",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "20"
        },
        "value": "%s"
    }
"""

PHOTOVOLTAIC_EXCESS_POWER: str = """
    {
        "name": "APPL.CtrlAppl.sParam.photovoltaics.ElectricEnergyMeter.values.power",
        "attributes": {
            "formatId": "fmt3p2",
            "longText": "Actual excess power",
            "unitId": "Pwr"
        },
        "value": "%s"
    }
"""

PHOTOVOLTAIC_DAILY_ENERGY: str = """
    {
        "name": "APPL.CtrlAppl.sParam.photovoltaics.ElectricEnergyMeter.values.heatDay",
        "attributes": {
            "formatId": "fmt6p1",
            "longText": "Energy per day",
            "unitId": "kWh"
        },
        "value": "%s"
    }
"""

PHOTOVOLTAIC_TOTAL_ENERGY: str = """
    {
        "name": "APPL.CtrlAppl.sParam.photovoltaics.ElectricEnergyMeter.values.accumulatedHeat",
        "attributes": {
            "formatId": "fmt6p0",
            "longText": "Acc. energy",
            "unitId": "kWh"
        },
        "value": "%s"
    }
"""

SYSTEM_HEAT_CIRCUIT_NUMBERS: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfHeatingCircuits",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty HC",
            "upperLimit": "8",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1
        },
        "value": "%s"
    }
"""

SYSTEM_SOLAR_CIRCUIT_NUMBERS: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfSolarCircuits",
        "attributes": {
            "dynLowerLimit": 1,
            "dynUpperLimit": 1,
            "formatId": "fmt2p0",
            "longText": "Qty solar",
            "upperLimit": "4",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

SYSTEM_HEAT_PUMP_NUMBERS: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfHeatPumps",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty heat pumps",
            "upperLimit": "4",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1
        },
        "value": "%s"
    }
"""

SYSTEM_BUFFER_TANK_NUMBERS: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfBuffers",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty buffers",
            "upperLimit": "0",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1
        },
        "value": "%s"
    }
"""

SYSTEM_HOT_WATER_TANK_NUMBERS: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfHotWaterTanks",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty HW tank",
            "upperLimit": "4",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1
        },
        "value": "%s"
    }
"""

SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfExtHeatSources",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty ext. heat sources",
            "upperLimit": "1",
            "lowerLimit": "0"
        },
        "value": "%s"
    }
"""

SYSTEM_OUTDOOR_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.outdoorTemp.values.actValue",
    "attributes": {
        "formatId": "fmtTemp",
        "longText": "Exterior temp.",
        "unitId": "Temp",
        "upperLimit": "100",
        "lowerLimit": "-100",
    },
    "value": "20.504164",
}

SYSTEM_OPERATING_MODE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.param.operatingMode",
    "attributes": {
        "formatId": "fmtOperatingMode",
        "longText": "Operating mode",
        "lowerLimit": "-1",
        "unitId": "Enum",
        "upperLimit": "4",
    },
    "value": "2",
}

DEVICE_INFO_RESPONSE: dict[str, Any] = {
    "ret": "OK",
    "revNo": 2,
    "orderNo": 000000,
    "serNo": 12345678,
    "name": "AP 440/H-A",
    "variantNo": 0,
}

SYSTEM_RESPONSE: dict[str, str] = {
    "ret": "OK",
    "name": "KeEnergy.MTec",
    "version": "2.2.2",
}

HMI_RESPONSE: dict[str, str] = {
    "ret": "OK",
    "name": "KeEnergy.WebHmi_2.2.0.0",
}

SYSTEM_HAS_PHOTOVOLTAICS: str = """
    {
        "name": "APPL.CtrlAppl.sParam.options.hasPhotovoltaics",
        "attributes": {"longText": "With photovoltaics"},
        "value": "%s"
    }
"""

SYSTEM_CPU_USAGE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sProcData.globalCpuTimePercent",
    "attributes": {
        "formatId": "fmt3p1",
        "longText": "CPU usage",
        "unitId": "Pct10",
    },
    "value": "27",
}

SYSTEM_WEBVIEW_CPU_USAGE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sProcData.processStatus[0].cpuTimePercent",
    "attributes": {
        "formatId": "fmt3p1",
        "longText": "WebView CPU",
        "unitId": "Pct10",
    },
    "value": "34",
}

SYSTEM_WEBSERVER_CPU_USAGE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sProcData.processStatus[1].cpuTimePercent",
    "attributes": {
        "formatId": "fmt3p1",
        "longText": "WebServer CPU",
        "unitId": "Pct10",
    },
    "value": "67",
}

SYSTEM_CONTROL_CPU_USAGE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sProcData.processStatus[2].cpuTimePercent",
    "attributes": {
        "formatId": "fmt3p1",
        "longText": "Ctrl CPU",
        "unitId": "Pct10",
    },
    "value": "7",
}

SYSTEM_RAM_USAGE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sProcData.RAMstatus.tmpfs",
    "attributes": {
        "formatId": "fmt6p0",
        "longText": "Used Temporary Memory",
        "unitId": "kB",
    },
    "value": "6432",
}

SYSTEM_FREE_RAM: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sProcData.totFreeRAM",
    "attributes": {
        "formatId": "fmt6p0",
        "longText": "Free RAM",
        "unitId": "kB",
    },
    "value": "100060",
}

DEFAULT_POSITION_RESPONSE: list[dict[str, Any]] = [
    json.loads(SYSTEM_HEAT_PUMP_NUMBERS % "1"),
    json.loads(SYSTEM_HEAT_CIRCUIT_NUMBERS % "1"),
    json.loads(SYSTEM_SOLAR_CIRCUIT_NUMBERS % "1"),
    json.loads(SYSTEM_BUFFER_TANK_NUMBERS % "1"),
    json.loads(SYSTEM_HOT_WATER_TANK_NUMBERS % "1"),
    json.loads(SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS % "1"),
]

MULTIPLE_POSITIONS_RESPONSE: list[dict[str, Any]] = [
    json.loads(SYSTEM_HEAT_PUMP_NUMBERS % "1"),
    json.loads(SYSTEM_HEAT_CIRCUIT_NUMBERS % "2"),
    json.loads(SYSTEM_SOLAR_CIRCUIT_NUMBERS % "2"),
    json.loads(SYSTEM_BUFFER_TANK_NUMBERS % "2"),
    json.loads(SYSTEM_HOT_WATER_TANK_NUMBERS % "2"),
    json.loads(SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS % "2"),
]

HEAT_PUMP_DATA: list[dict[str, Any]] = [
    HEAT_PUMP_CIRCULATION_PUMP,
    HEAT_PUMP_SOURCE_PUMP_SPEED,
    HEAT_PUMP_COMPRESSOR,
    HEAT_PUMP_COMPRESSOR_NIGHT_SPEED,
    HEAT_PUMP_COMPRESSOR_INPUT_TEMPERATURE,
    HEAT_PUMP_COMPRESSOR_OUTPUT_TEMPERATURE,
    HEAT_PUMP_COMPRESSOR_USE_NIGHT_SPEED,
    HEAT_PUMP_CONDENSER_TEMPERATURE,
    HEAT_PUMP_VAPORIZER_TEMPERATURE,
    HEAT_PUMP_HEAT_REQUEST,
    HEAT_PUMP_HIGH_PRESSURE,
    HEAT_PUMP_FLOW_TEMPERATURE,
    HEAT_PUMP_LOW_PRESSURE,
    HEAT_PUMP_NAME,
    HEAT_PUMP_RETURN_FLOW_TEMPERATURE,
    HEAT_PUMP_SOURCE_INPUT_TEMPERATURE,
    HEAT_PUMP_SOURCE_OUTPUT_TEMPERATURE,
    HEAT_PUMP_STATE,
    HEAT_PUMP_SUBSTATE,
    HEAT_PUMP_COMPRESSOR_POWER,
    HEAT_PUMP_HEATING_POWER,
    HEAT_PUMP_HOT_WATER_POWER,
    HEAT_PUMP_COP,
    HEAT_PUMP_HEATING_ENERGY,
    HEAT_PUMP_HEATING_ENERGY_CONSUMPTION,
    HEAT_PUMP_HEATING_SPF,
    HEAT_PUMP_COOLING_ENERGY,
    HEAT_PUMP_COOLING_ENERGY_CONSUMPTION,
    HEAT_PUMP_COOLING_SPF,
    HEAT_PUMP_HOT_WATER_ENERGY,
    HEAT_PUMP_HOT_WATER_ENERGY_CONSUMPTION,
    HEAT_PUMP_HOT_WATER_SPF,
    HEAT_PUMP_TOTAL_THERMAL_ENERGY,
    HEAT_PUMP_TOTAL_ENERGY_CONSUMPTION,
    HEAT_PUMP_TOTAL_SPF,
    HEAT_PUMP_OPERATING_TIME,
    HEAT_PUMP_MAX_RUNTIME,
    HEAT_PUMP_ACTIVATION_COUNTER,
]

DEFAULT_POSITION_FIXED_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(SYSTEM_HAS_PHOTOVOLTAICS % "true"),
    json.loads(HEAT_CIRCUIT_HAS_ROOM_TEMPERATURE % ("0", "true")),
    json.loads(HEAT_CIRCUIT_HAS_ROOM_HUMIDITY % ("0", "true")),
    json.loads(HEAT_PUMP_HAS_PASSIVE_COOLING % "true"),
]


def get_multiple_position_fixed_data_response(has_passive_cooling: str = "false") -> list[dict[str, Any]]:
    return [
        json.loads(SYSTEM_HAS_PHOTOVOLTAICS % "true"),
        json.loads(HEAT_CIRCUIT_HAS_ROOM_TEMPERATURE % ("0", "true")),
        json.loads(HEAT_CIRCUIT_HAS_ROOM_TEMPERATURE % ("1", "false")),
        json.loads(HEAT_CIRCUIT_HAS_ROOM_HUMIDITY % ("0", "true")),
        json.loads(HEAT_CIRCUIT_HAS_ROOM_HUMIDITY % ("1", "false")),
        json.loads(HEAT_PUMP_HAS_PASSIVE_COOLING % f"{has_passive_cooling}"),
    ]


DEFAULT_POSITION_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_MODE % ("0", "1")),
    json.loads(EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE % ("0", "1")),
    json.loads(EXTERNAL_HEAT_SOURCE_HEAT_REQUEST % ("0", "true")),
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_TIME % ("0", "812999")),
    json.loads(EXTERNAL_HEAT_SOURCE_MAX_RUNTIME % ("0", "8129")),
    json.loads(EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER % ("0", "812")),
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT % ("0", "26.5543")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE % ("0", "24.33543")),
    json.loads(HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE % ("0", "22.2143")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_DAY % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY % ("0", "18")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_NIGHT % ("0", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "3")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET % ("0", "1.5")),
    json.loads(SOLAR_CIRCUIT_OPERATION_MODE % ("0", "0")),
    json.loads(SOLAR_CIRCUIT_SOURCE_TEMPERATURE % ("0", "44.43")),
    json.loads(SOLAR_CIRCUIT_PUMP_1 % ("0", "0.63")),
    json.loads(SOLAR_CIRCUIT_PUMP_2 % ("0", "0.43")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1 % ("0", "36.76")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2 % ("1", "26.76")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_1 % ("0", "55")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_2 % ("1", "55")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("0", "true")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("1", "false")),
    json.loads(SOLAR_CIRCUIT_HEATING_ENERGY % ("0", "8.73")),
    json.loads(SOLAR_CIRCUIT_DAILY_ENERGY % ("0", "2.33")),
    json.loads(SOLAR_CIRCUIT_ACTUAL_POWER % ("0", "3452")),
    json.loads(SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2 % ("0", "true")),
    *HEAT_PUMP_DATA,
    json.loads(BUFFER_TANK_CURRENT_TOP_TEMPERATURE % ("0", "45.67")),
    json.loads(BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE % ("0", "25.67")),
    json.loads(BUFFER_TANK_OPERATING_MODE % ("0", "0")),
    json.loads(BUFFER_TANK_STANDBY_TEMPERATURE % ("0", "10.00")),
    json.loads(BUFFER_TANK_TARGET_TEMPERATURE % ("0", "44.00")),
    json.loads(BUFFER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(BUFFER_TANK_COOL_REQUEST % ("0", "true")),
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_HOT_WATER_FLOW % ("0", "false")),
    json.loads(HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_TARGET_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_STANDBY_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_CURRENT_TEMPERATURE % ("0", "47.700001")),
    json.loads(PHOTOVOLTAIC_EXCESS_POWER % "437.700001"),
    json.loads(PHOTOVOLTAIC_DAILY_ENERGY % "437.700001"),
    json.loads(PHOTOVOLTAIC_TOTAL_ENERGY % "437.700001"),
    SYSTEM_OUTDOOR_TEMPERATURE,
    SYSTEM_OPERATING_MODE,
    SYSTEM_CPU_USAGE,
    SYSTEM_WEBVIEW_CPU_USAGE,
    SYSTEM_WEBSERVER_CPU_USAGE,
    SYSTEM_CONTROL_CPU_USAGE,
    SYSTEM_RAM_USAGE,
    SYSTEM_FREE_RAM,
]

ENTITY_UPDATED_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_MODE % ("0", "1")),
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_MODE % ("1", "0")),
    json.loads(EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE % ("0", "13")),
    json.loads(EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE % ("1", "12")),
    json.loads(EXTERNAL_HEAT_SOURCE_HEAT_REQUEST % ("0", "true")),
    json.loads(EXTERNAL_HEAT_SOURCE_HEAT_REQUEST % ("1", "true")),
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_TIME % ("0", "812999")),
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_TIME % ("1", "812999")),
    json.loads(EXTERNAL_HEAT_SOURCE_MAX_RUNTIME % ("0", "8129")),
    json.loads(EXTERNAL_HEAT_SOURCE_MAX_RUNTIME % ("1", "8129")),
    json.loads(EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER % ("0", "812")),
    json.loads(EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER % ("1", "812")),
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("1", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("1", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("1", "13.1")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT % ("0", "26.5543")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT % ("1", "26.5543")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE % ("0", "24.33543")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE % ("1", "24.33543")),
    json.loads(HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE % ("0", "22.2143")),
    json.loads(HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE % ("1", "22.2143")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY % ("1", "20.5")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_DAY % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_DAY % ("1", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("1", "0")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY % ("0", "18")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY % ("1", "18")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT % ("0", "20")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT % ("1", "20")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_NIGHT % ("0", "18")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_NIGHT % ("1", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "3")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("1", "1")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE % ("1", "20.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET % ("0", "1.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET % ("1", "0")),
    json.loads(SOLAR_CIRCUIT_OPERATION_MODE % ("0", "0")),
    json.loads(SOLAR_CIRCUIT_OPERATION_MODE % ("1", "1")),
    json.loads(SOLAR_CIRCUIT_SOURCE_TEMPERATURE % ("0", "44.43")),
    json.loads(SOLAR_CIRCUIT_SOURCE_TEMPERATURE % ("1", "34.43")),
    json.loads(SOLAR_CIRCUIT_PUMP_1 % ("0", "0.63")),
    json.loads(SOLAR_CIRCUIT_PUMP_1 % ("1", "0.67")),
    json.loads(SOLAR_CIRCUIT_PUMP_2 % ("0", "0.43")),
    json.loads(SOLAR_CIRCUIT_PUMP_2 % ("1", "0.53")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1 % ("0", "36.76")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2 % ("1", "26.76")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1 % ("2", "36.76")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2 % ("3", "26.76")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_1 % ("0", "55")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_2 % ("1", "55")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_1 % ("2", "55")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_2 % ("3", "55")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("0", "true")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("1", "false")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("2", "true")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("3", "false")),
    json.loads(SOLAR_CIRCUIT_HEATING_ENERGY % ("0", "8.73")),
    json.loads(SOLAR_CIRCUIT_HEATING_ENERGY % ("1", "8.73")),
    json.loads(SOLAR_CIRCUIT_DAILY_ENERGY % ("0", "2.33")),
    json.loads(SOLAR_CIRCUIT_DAILY_ENERGY % ("1", "2.33")),
    json.loads(SOLAR_CIRCUIT_ACTUAL_POWER % ("0", "3452")),
    json.loads(SOLAR_CIRCUIT_ACTUAL_POWER % ("1", "3452")),
    json.loads(SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2 % ("0", "true")),
    json.loads(SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2 % ("1", "false")),
    *HEAT_PUMP_DATA,
    json.loads(BUFFER_TANK_CURRENT_TOP_TEMPERATURE % ("0", "45.67")),
    json.loads(BUFFER_TANK_CURRENT_TOP_TEMPERATURE % ("1", "35.67")),
    json.loads(BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE % ("0", "25.67")),
    json.loads(BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE % ("1", "15.67")),
    json.loads(BUFFER_TANK_OPERATING_MODE % ("0", "0")),
    json.loads(BUFFER_TANK_OPERATING_MODE % ("1", "1")),
    json.loads(BUFFER_TANK_STANDBY_TEMPERATURE % ("0", "10.00")),
    json.loads(BUFFER_TANK_STANDBY_TEMPERATURE % ("1", "11.00")),
    json.loads(BUFFER_TANK_TARGET_TEMPERATURE % ("0", "44.00")),
    json.loads(BUFFER_TANK_TARGET_TEMPERATURE % ("1", "43.00")),
    json.loads(BUFFER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(BUFFER_TANK_HEAT_REQUEST % ("1", "true")),
    json.loads(BUFFER_TANK_COOL_REQUEST % ("0", "true")),
    json.loads(BUFFER_TANK_COOL_REQUEST % ("1", "false")),
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("1", "true")),
    json.loads(HOT_WATER_TANK_HOT_WATER_FLOW % ("0", "false")),
    json.loads(HOT_WATER_TANK_HOT_WATER_FLOW % ("1", "true")),
    json.loads(HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE % ("0", "51.23")),
    json.loads(HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE % ("1", "51.23")),
    json.loads(HOT_WATER_TANK_TARGET_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_TARGET_TEMPERATURE % ("1", "51")),
    json.loads(HOT_WATER_TANK_STANDBY_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_STANDBY_TEMPERATURE % ("1", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "0")),
    json.loads(HOT_WATER_CURRENT_TEMPERATURE % ("0", "47.700001")),
    json.loads(HOT_WATER_CURRENT_TEMPERATURE % ("1", "47.700001")),
    json.loads(PHOTOVOLTAIC_EXCESS_POWER % "437.700001"),
    json.loads(PHOTOVOLTAIC_DAILY_ENERGY % "437.700001"),
    json.loads(PHOTOVOLTAIC_TOTAL_ENERGY % "437.700001"),
    SYSTEM_OUTDOOR_TEMPERATURE,
    SYSTEM_OPERATING_MODE,
    SYSTEM_CPU_USAGE,
    SYSTEM_WEBVIEW_CPU_USAGE,
    SYSTEM_WEBSERVER_CPU_USAGE,
    SYSTEM_CONTROL_CPU_USAGE,
    SYSTEM_RAM_USAGE,
    SYSTEM_FREE_RAM,
]

HEAT_CIRCUIT_OPERATION_MODE_3_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_MODE % ("0", "1")),
    json.loads(EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE % ("0", "23")),
    json.loads(EXTERNAL_HEAT_SOURCE_HEAT_REQUEST % ("0", "true")),
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_TIME % ("0", "812999")),
    json.loads(EXTERNAL_HEAT_SOURCE_MAX_RUNTIME % ("0", "8129")),
    json.loads(EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER % ("0", "812")),
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT % ("0", "26.5543")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE % ("0", "24.33543")),
    json.loads(HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE % ("0", "22.2143")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_DAY % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY % ("0", "18")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_NIGHT % ("0", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "3")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET % ("0", "1.5")),
    json.loads(SOLAR_CIRCUIT_OPERATION_MODE % ("0", "0")),
    json.loads(SOLAR_CIRCUIT_SOURCE_TEMPERATURE % ("0", "44.43")),
    json.loads(SOLAR_CIRCUIT_PUMP_1 % ("0", "0.63")),
    json.loads(SOLAR_CIRCUIT_PUMP_2 % ("0", "0.43")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1 % ("0", "36.76")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2 % ("1", "26.76")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_1 % ("0", "55")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_2 % ("1", "55")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("0", "true")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("1", "false")),
    json.loads(SOLAR_CIRCUIT_HEATING_ENERGY % ("0", "8.73")),
    json.loads(SOLAR_CIRCUIT_DAILY_ENERGY % ("0", "2.33")),
    json.loads(SOLAR_CIRCUIT_ACTUAL_POWER % ("0", "3452")),
    json.loads(SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2 % ("0", "true")),
    *HEAT_PUMP_DATA,
    json.loads(BUFFER_TANK_CURRENT_TOP_TEMPERATURE % ("0", "45.67")),
    json.loads(BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE % ("0", "25.67")),
    json.loads(BUFFER_TANK_OPERATING_MODE % ("0", "0")),
    json.loads(BUFFER_TANK_STANDBY_TEMPERATURE % ("0", "10.00")),
    json.loads(BUFFER_TANK_TARGET_TEMPERATURE % ("0", "44.00")),
    json.loads(BUFFER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(BUFFER_TANK_COOL_REQUEST % ("0", "true")),
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_HOT_WATER_FLOW % ("0", "true")),
    json.loads(HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_TARGET_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_STANDBY_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_CURRENT_TEMPERATURE % ("0", "47.700001")),
    json.loads(PHOTOVOLTAIC_EXCESS_POWER % "437.700001"),
    json.loads(PHOTOVOLTAIC_DAILY_ENERGY % "437.700001"),
    json.loads(PHOTOVOLTAIC_TOTAL_ENERGY % "437.700001"),
    SYSTEM_OUTDOOR_TEMPERATURE,
    SYSTEM_OPERATING_MODE,
    SYSTEM_CPU_USAGE,
    SYSTEM_WEBVIEW_CPU_USAGE,
    SYSTEM_WEBSERVER_CPU_USAGE,
    SYSTEM_CONTROL_CPU_USAGE,
    SYSTEM_RAM_USAGE,
    SYSTEM_FREE_RAM,
]

HEAT_CIRCUIT_OPERATION_MODE_4_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_MODE % ("0", "1")),
    json.loads(EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE % ("0", "12.22")),
    json.loads(EXTERNAL_HEAT_SOURCE_HEAT_REQUEST % ("0", "true")),
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_TIME % ("0", "812999")),
    json.loads(EXTERNAL_HEAT_SOURCE_MAX_RUNTIME % ("0", "8129")),
    json.loads(EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER % ("0", "812")),
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT % ("0", "26.5543")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE % ("0", "24.33543")),
    json.loads(HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE % ("0", "22.2143")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_DAY % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY % ("0", "18")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_NIGHT % ("0", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "4")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET % ("0", "1.5")),
    json.loads(SOLAR_CIRCUIT_OPERATION_MODE % ("0", "0")),
    json.loads(SOLAR_CIRCUIT_SOURCE_TEMPERATURE % ("0", "44.43")),
    json.loads(SOLAR_CIRCUIT_PUMP_1 % ("0", "0.63")),
    json.loads(SOLAR_CIRCUIT_PUMP_2 % ("0", "0.43")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1 % ("0", "36.76")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2 % ("1", "26.76")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_1 % ("0", "55")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_2 % ("1", "55")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("0", "true")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("1", "false")),
    json.loads(SOLAR_CIRCUIT_HEATING_ENERGY % ("0", "8.73")),
    json.loads(SOLAR_CIRCUIT_DAILY_ENERGY % ("0", "2.33")),
    json.loads(SOLAR_CIRCUIT_ACTUAL_POWER % ("0", "3452")),
    json.loads(SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2 % ("0", "true")),
    *HEAT_PUMP_DATA,
    json.loads(BUFFER_TANK_CURRENT_TOP_TEMPERATURE % ("0", "45.67")),
    json.loads(BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE % ("0", "25.67")),
    json.loads(BUFFER_TANK_OPERATING_MODE % ("0", "0")),
    json.loads(BUFFER_TANK_STANDBY_TEMPERATURE % ("0", "10.00")),
    json.loads(BUFFER_TANK_TARGET_TEMPERATURE % ("0", "44.00")),
    json.loads(BUFFER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(BUFFER_TANK_COOL_REQUEST % ("0", "true")),
    json.loads(HOT_WATER_TANK_HOT_WATER_FLOW % ("0", "true")),
    json.loads(HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_TARGET_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_STANDBY_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_CURRENT_TEMPERATURE % ("0", "47.700001")),
    json.loads(PHOTOVOLTAIC_EXCESS_POWER % "437.700001"),
    json.loads(PHOTOVOLTAIC_DAILY_ENERGY % "437.700001"),
    json.loads(PHOTOVOLTAIC_TOTAL_ENERGY % "437.700001"),
    SYSTEM_OUTDOOR_TEMPERATURE,
    SYSTEM_OPERATING_MODE,
    SYSTEM_CPU_USAGE,
    SYSTEM_WEBVIEW_CPU_USAGE,
    SYSTEM_WEBSERVER_CPU_USAGE,
    SYSTEM_CONTROL_CPU_USAGE,
    SYSTEM_RAM_USAGE,
    SYSTEM_FREE_RAM,
]

MULTIPLE_POSITIONS_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_MODE % ("0", "0")),
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_MODE % ("1", "1")),
    json.loads(EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE % ("0", "17.23")),
    json.loads(EXTERNAL_HEAT_SOURCE_TARGET_TEMPERATURE % ("1", "17.23")),
    json.loads(EXTERNAL_HEAT_SOURCE_HEAT_REQUEST % ("0", "true")),
    json.loads(EXTERNAL_HEAT_SOURCE_HEAT_REQUEST % ("1", "true")),
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_TIME % ("0", "812999")),
    json.loads(EXTERNAL_HEAT_SOURCE_OPERATING_TIME % ("1", "812999")),
    json.loads(EXTERNAL_HEAT_SOURCE_MAX_RUNTIME % ("0", "8129")),
    json.loads(EXTERNAL_HEAT_SOURCE_MAX_RUNTIME % ("1", "8129")),
    json.loads(EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER % ("0", "812")),
    json.loads(EXTERNAL_HEAT_SOURCE_ACTIVATION_COUNTER % ("1", "812")),
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("1", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("1", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("1", "13.1")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT % ("0", "26.5543")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE_SETPOINT % ("1", "26.5543")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE % ("0", "24.33543")),
    json.loads(HEAT_CIRCUIT_FLOW_TEMPERATURE % ("1", "24.33543")),
    json.loads(HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE % ("0", "22.2143")),
    json.loads(HEAT_CIRCUIT_RETURN_FLOW_TEMPERATURE % ("1", "22.2143")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_DAY % ("1", "20.5")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_DAY % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_DAY % ("1", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("1", "0")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY % ("0", "18")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_AWAY % ("1", "18")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT % ("0", "20")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_NIGHT % ("1", "20")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_NIGHT % ("0", "18")),
    json.loads(HEAT_CIRCUIT_HEATING_LIMIT_NIGHT % ("1", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "2")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("1", "0")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE % ("1", "20.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET % ("0", "1.5")),
    json.loads(HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET % ("1", "0")),
    json.loads(SOLAR_CIRCUIT_OPERATION_MODE % ("0", "0")),
    json.loads(SOLAR_CIRCUIT_OPERATION_MODE % ("1", "1")),
    json.loads(SOLAR_CIRCUIT_SOURCE_TEMPERATURE % ("0", "44.43")),
    json.loads(SOLAR_CIRCUIT_SOURCE_TEMPERATURE % ("1", "34.43")),
    json.loads(SOLAR_CIRCUIT_PUMP_1 % ("0", "0.63")),
    json.loads(SOLAR_CIRCUIT_PUMP_1 % ("1", "0.43")),
    json.loads(SOLAR_CIRCUIT_PUMP_2 % ("0", "0.73")),
    json.loads(SOLAR_CIRCUIT_PUMP_2 % ("1", "0.53")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1 % ("0", "36.76")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2 % ("1", "26.76")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_1 % ("2", "46.76")),
    json.loads(SOLAR_CIRCUIT_CURRENT_TEMPERATURE_2 % ("3", "56.76")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_1 % ("0", "55")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_2 % ("1", "54")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_1 % ("2", "53")),
    json.loads(SOLAR_CIRCUIT_TARGET_TEMPERATURE_2 % ("3", "52")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("0", "true")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("1", "false")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("2", "false")),
    json.loads(SOLAR_CIRCUIT_HEAT_REQUEST % ("3", "true")),
    json.loads(SOLAR_CIRCUIT_HEATING_ENERGY % ("0", "8.73")),
    json.loads(SOLAR_CIRCUIT_HEATING_ENERGY % ("1", "4.73")),
    json.loads(SOLAR_CIRCUIT_DAILY_ENERGY % ("0", "2.33")),
    json.loads(SOLAR_CIRCUIT_DAILY_ENERGY % ("1", "3.33")),
    json.loads(SOLAR_CIRCUIT_ACTUAL_POWER % ("0", "3452")),
    json.loads(SOLAR_CIRCUIT_ACTUAL_POWER % ("1", "2452")),
    json.loads(SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2 % ("0", "false")),
    json.loads(SOLAR_CIRCUIT_PRIORITY_1_BEFORE_2 % ("1", "true")),
    *HEAT_PUMP_DATA,
    json.loads(BUFFER_TANK_CURRENT_TOP_TEMPERATURE % ("0", "45.67")),
    json.loads(BUFFER_TANK_CURRENT_TOP_TEMPERATURE % ("1", "35.67")),
    json.loads(BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE % ("0", "15.67")),
    json.loads(BUFFER_TANK_CURRENT_BOTTOM_TEMPERATURE % ("1", "25.67")),
    json.loads(BUFFER_TANK_OPERATING_MODE % ("0", "0")),
    json.loads(BUFFER_TANK_OPERATING_MODE % ("1", "1")),
    json.loads(BUFFER_TANK_STANDBY_TEMPERATURE % ("0", "10.00")),
    json.loads(BUFFER_TANK_STANDBY_TEMPERATURE % ("1", "11.00")),
    json.loads(BUFFER_TANK_TARGET_TEMPERATURE % ("0", "44.00")),
    json.loads(BUFFER_TANK_TARGET_TEMPERATURE % ("1", "43.00")),
    json.loads(BUFFER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(BUFFER_TANK_HEAT_REQUEST % ("1", "true")),
    json.loads(BUFFER_TANK_COOL_REQUEST % ("0", "true")),
    json.loads(BUFFER_TANK_COOL_REQUEST % ("1", "false")),
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("1", "true")),
    json.loads(HOT_WATER_TANK_HOT_WATER_FLOW % ("0", "false")),
    json.loads(HOT_WATER_TANK_HOT_WATER_FLOW % ("1", "true")),
    json.loads(HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE % ("0", "51.23")),
    json.loads(HOT_WATER_TANK_FRESH_WATER_MODULE_TEMPERATURE % ("1", "51.23")),
    json.loads(HOT_WATER_TANK_TARGET_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_TARGET_TEMPERATURE % ("1", "51")),
    json.loads(HOT_WATER_TANK_STANDBY_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_STANDBY_TEMPERATURE % ("1", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "0")),
    json.loads(HOT_WATER_CURRENT_TEMPERATURE % ("0", "47.700001")),
    json.loads(HOT_WATER_CURRENT_TEMPERATURE % ("1", "47.700001")),
    json.loads(PHOTOVOLTAIC_EXCESS_POWER % "437.700001"),
    json.loads(PHOTOVOLTAIC_DAILY_ENERGY % "437.700001"),
    json.loads(PHOTOVOLTAIC_TOTAL_ENERGY % "437.700001"),
    SYSTEM_OUTDOOR_TEMPERATURE,
    SYSTEM_OPERATING_MODE,
    SYSTEM_CPU_USAGE,
    SYSTEM_WEBVIEW_CPU_USAGE,
    SYSTEM_WEBSERVER_CPU_USAGE,
    SYSTEM_CONTROL_CPU_USAGE,
    SYSTEM_RAM_USAGE,
    SYSTEM_FREE_RAM,
]
