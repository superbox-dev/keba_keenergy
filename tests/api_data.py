import json
from typing import Any

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

HEAT_CIRCUIT_DAY_TEMPERATURE: str = """
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

HEAT_CIRCUIT_DAY_TEMPERATURE_THRESHOLD: str = """
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

HEAT_CIRCUIT_HOLIDAY_TEMPERATURE: str = """
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

HEAT_CIRCUIT_NAME: str = """
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[%s].param.name",
        "attributes": {"longText": "Designation"},
        "value": "%s"
    }
"""

HEAT_CIRCUIT_NIGHT_TEMPERATURE: str = """
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

HEAT_CIRCUIT_NIGHT_TEMPERATURE_THRESHOLD: str = """
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

HEAT_CIRCUIT_TEMPERATURE: str = """
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

HEAT_CIRCUIT_TEMPERATURE_OFFSET: str = """
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

HEAT_PUMP_COMPRESSOR_INPUT_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempCompressorIn.values.actValue",
    "attributes": {"formatId": "fmtTemp", "longText": "Comp. in temp.", "unitId": "Temp"},
    "value": "27.200001",
}

HEAT_PUMP_COMPRESSOR_OUTPUT_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempCompressorOut.values.actValue",
    "attributes": {"formatId": "fmtTemp", "longText": "Comp. out temp.", "unitId": "Temp"},
    "value": "27.200001",
}

HEAT_PUMP_HEAT_REQUEST: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].values.request",
    "attributes": {"longText": "Heat pump request"},
    "value": "false",
}

HEAT_PUMP_HIGH_PRESSURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].HighPressure.values.actValue",
    "attributes": {"formatId": "fmt3p2", "longText": "High pressure", "unitId": "PressBar"},
    "value": "15.61875",
}

HEAT_PUMP_LOW_PRESSURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].LowPressure.values.actValue",
    "attributes": {"formatId": "fmt3p2", "longText": "Low pressure", "unitId": "PressBar"},
    "value": "15.354687",
}

HEAT_PUMP_INFLOW_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempHeatFlow.values.actValue",
    "attributes": {"formatId": "fmtTemp", "longText": "Inflow temp.", "unitId": "Temp"},
    "value": "24.800001",
}

HEAT_PUMP_REFLUX_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempHeatReflux.values.actValue",
    "attributes": {"formatId": "fmtTemp", "longText": "Reflux temp.", "unitId": "Temp"},
    "value": "23.9",
}

HEAT_PUMP_NAME: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].param.name",
    "attributes": {"longText": "Name"},
    "value": "WPS26",
}

HEAT_PUMP_SOURCE_INPUT_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempSourceIn.values.actValue",
    "attributes": {"formatId": "fmtTemp", "longText": "Source in temp.", "unitId": "Temp"},
    "value": "25.700001",
}

HEAT_PUMP_SOURCE_OUTPUT_TEMPERATURE: dict[str, Any] = {
    "name": "APPL.CtrlAppl.sParam.heatpump[0].TempSourceOut.values.actValue",
    "attributes": {"formatId": "fmtTemp", "longText": "Source out temp.", "unitId": "Temp"},
    "value": "24.9",
}

HEAT_PUMP_STATUS: dict[str, Any] = {
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

HOT_WATER_TANK_HEAT_REQUEST: str = """
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[%s].values.heatRequestTop",
        "attributes": {"longText": "Heat requirement"},
        "value": "%s"
    }
"""

HOT_WATER_TANK_LOW_LIMIT_TEMPERATURE: str = """
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

HOT_WATER_TANK_MIN_TEMPERATURE: str = """
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

HOT_WATER_TEMPERATURE: str = """
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

SYSTEM_HEAT_CIRCUIT_POSITIONS: str = """
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

SYSTEM_HEAT_PUMP_POSITIONS: str = """
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

SYSTEM_HOT_WATER_TANK_POSITIONS: str = """
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

SYSTEM_TEMPERATURE_OUTSIDE: dict[str, Any] = {
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

DEFAULT_POSITION_RESPONSE: list[dict[str, Any]] = [
    json.loads(SYSTEM_HEAT_PUMP_POSITIONS % "1"),
    json.loads(SYSTEM_HEAT_CIRCUIT_POSITIONS % "1"),
    json.loads(SYSTEM_HOT_WATER_TANK_POSITIONS % "1"),
]

MULTIPLE_POSITIONS_RESPONSE: list[dict[str, Any]] = [
    json.loads(SYSTEM_HEAT_PUMP_POSITIONS % "1"),
    json.loads(SYSTEM_HEAT_CIRCUIT_POSITIONS % "2"),
    json.loads(SYSTEM_HOT_WATER_TANK_POSITIONS % "2"),
]

HEAT_PUMP_DATA: list[dict[str, Any]] = [
    HEAT_PUMP_CIRCULATION_PUMP,
    HEAT_PUMP_COMPRESSOR,
    HEAT_PUMP_COMPRESSOR_INPUT_TEMPERATURE,
    HEAT_PUMP_COMPRESSOR_OUTPUT_TEMPERATURE,
    HEAT_PUMP_HEAT_REQUEST,
    HEAT_PUMP_HIGH_PRESSURE,
    HEAT_PUMP_INFLOW_TEMPERATURE,
    HEAT_PUMP_LOW_PRESSURE,
    HEAT_PUMP_NAME,
    HEAT_PUMP_REFLUX_TEMPERATURE,
    HEAT_PUMP_SOURCE_INPUT_TEMPERATURE,
    HEAT_PUMP_SOURCE_OUTPUT_TEMPERATURE,
    HEAT_PUMP_STATUS,
]

DEFAULT_POSITION_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE_THRESHOLD % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_HOLIDAY_TEMPERATURE % ("0", "18")),
    json.loads(HEAT_CIRCUIT_NAME % ("0", "FBH1")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE % ("0", "20")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE_THRESHOLD % ("0", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "3")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE_OFFSET % ("0", "1.5")),
    *HEAT_PUMP_DATA,
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_LOW_LIMIT_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_MIN_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_TEMPERATURE % ("0", "47.700001")),
    json.loads(SYSTEM_HEAT_CIRCUIT_POSITIONS % "1"),
    json.loads(SYSTEM_HEAT_PUMP_POSITIONS % "1"),
    json.loads(SYSTEM_HOT_WATER_TANK_POSITIONS % "1"),
    SYSTEM_TEMPERATURE_OUTSIDE,
]

MULTIPLE_POSITIONS_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("1", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("1", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("1", "13.1")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE % ("1", "20.5")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE_THRESHOLD % ("0", "20")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE_THRESHOLD % ("1", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("1", "0")),
    json.loads(HEAT_CIRCUIT_HOLIDAY_TEMPERATURE % ("0", "18")),
    json.loads(HEAT_CIRCUIT_HOLIDAY_TEMPERATURE % ("1", "18")),
    json.loads(HEAT_CIRCUIT_NAME % ("0", "FBH1")),
    json.loads(HEAT_CIRCUIT_NAME % ("1", "FBH2")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE % ("0", "20")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE % ("1", "20")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE_THRESHOLD % ("0", "18")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE_THRESHOLD % ("1", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "2")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("1", "0")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE % ("1", "20.5")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE_OFFSET % ("0", "1.5")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE_OFFSET % ("1", "0")),
    *HEAT_PUMP_DATA,
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "true")),
    json.loads(HOT_WATER_TANK_LOW_LIMIT_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_LOW_LIMIT_TEMPERATURE % ("1", "51")),
    json.loads(HOT_WATER_TANK_MIN_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_MIN_TEMPERATURE % ("1", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "0")),
    json.loads(HOT_WATER_TEMPERATURE % ("0", "47.700001")),
    json.loads(HOT_WATER_TEMPERATURE % ("1", "47.700001")),
    json.loads(SYSTEM_HEAT_CIRCUIT_POSITIONS % "2"),
    json.loads(SYSTEM_HEAT_PUMP_POSITIONS % "1"),
    json.loads(SYSTEM_HOT_WATER_TANK_POSITIONS % "2"),
    SYSTEM_TEMPERATURE_OUTSIDE,
]

ENTITY_UPDATED_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("1", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("1", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("1", "13.1")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE % ("1", "20.5")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE_THRESHOLD % ("0", "20")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE_THRESHOLD % ("1", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("1", "0")),
    json.loads(HEAT_CIRCUIT_HOLIDAY_TEMPERATURE % ("0", "18")),
    json.loads(HEAT_CIRCUIT_HOLIDAY_TEMPERATURE % ("1", "18")),
    json.loads(HEAT_CIRCUIT_NAME % ("0", "FBH1")),
    json.loads(HEAT_CIRCUIT_NAME % ("1", "FBH2")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE % ("0", "20")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE % ("1", "20")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE_THRESHOLD % ("0", "18")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE_THRESHOLD % ("1", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "3")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("1", "1")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE % ("1", "20.5")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE_OFFSET % ("0", "1.5")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE_OFFSET % ("1", "0")),
    *HEAT_PUMP_DATA,
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "true")),
    json.loads(HOT_WATER_TANK_LOW_LIMIT_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_LOW_LIMIT_TEMPERATURE % ("1", "51")),
    json.loads(HOT_WATER_TANK_MIN_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_MIN_TEMPERATURE % ("1", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "0")),
    json.loads(HOT_WATER_TEMPERATURE % ("0", "47.700001")),
    json.loads(HOT_WATER_TEMPERATURE % ("1", "47.700001")),
    json.loads(SYSTEM_HEAT_CIRCUIT_POSITIONS % "2"),
    json.loads(SYSTEM_HEAT_PUMP_POSITIONS % "1"),
    json.loads(SYSTEM_HOT_WATER_TANK_POSITIONS % "2"),
    SYSTEM_TEMPERATURE_OUTSIDE,
]

HEAT_CIRCUIT_OPERATION_MODE_3_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE_THRESHOLD % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_HOLIDAY_TEMPERATURE % ("0", "18")),
    json.loads(HEAT_CIRCUIT_NAME % ("0", "FBH1")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE % ("0", "20")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE_THRESHOLD % ("0", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "3")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE_OFFSET % ("0", "1.5")),
    *HEAT_PUMP_DATA,
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_LOW_LIMIT_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_MIN_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_TEMPERATURE % ("0", "47.700001")),
    json.loads(SYSTEM_HEAT_CIRCUIT_POSITIONS % "1"),
    json.loads(SYSTEM_HEAT_PUMP_POSITIONS % "1"),
    json.loads(SYSTEM_HOT_WATER_TANK_POSITIONS % "1"),
    SYSTEM_TEMPERATURE_OUTSIDE,
]

HEAT_CIRCUIT_OPERATION_MODE_4_DATA_RESPONSE: list[dict[str, Any]] = [
    json.loads(HEAT_CIRCUIT_ROOM_TEMPERATURE % ("0", "22.42")),
    json.loads(HEAT_CIRCUIT_ROOM_HUMIDITY % ("0", "53")),
    json.loads(HEAT_CIRCUIT_DEW_POINT % ("0", "13.1")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_DAY_TEMPERATURE_THRESHOLD % ("0", "20")),
    json.loads(HEAT_CIRCUIT_HEAT_REQUEST % ("0", "1")),
    json.loads(HEAT_CIRCUIT_HOLIDAY_TEMPERATURE % ("0", "18")),
    json.loads(HEAT_CIRCUIT_NAME % ("0", "FBH1")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE % ("0", "20")),
    json.loads(HEAT_CIRCUIT_NIGHT_TEMPERATURE_THRESHOLD % ("0", "18")),
    json.loads(HEAT_CIRCUIT_OPERATION_MODE % ("0", "4")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE % ("0", "20.5")),
    json.loads(HEAT_CIRCUIT_TEMPERATURE_OFFSET % ("0", "1.5")),
    *HEAT_PUMP_DATA,
    json.loads(HOT_WATER_TANK_HEAT_REQUEST % ("0", "false")),
    json.loads(HOT_WATER_TANK_LOW_LIMIT_TEMPERATURE % ("0", "51")),
    json.loads(HOT_WATER_TANK_MIN_TEMPERATURE % ("0", "32.5")),
    json.loads(HOT_WATER_TANK_OPERATION_MODE % ("0", "3")),
    json.loads(HOT_WATER_TEMPERATURE % ("0", "47.700001")),
    json.loads(SYSTEM_HEAT_CIRCUIT_POSITIONS % "1"),
    json.loads(SYSTEM_HEAT_PUMP_POSITIONS % "1"),
    json.loads(SYSTEM_HOT_WATER_TANK_POSITIONS % "1"),
    SYSTEM_TEMPERATURE_OUTSIDE,
]
