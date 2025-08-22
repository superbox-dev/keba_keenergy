from typing import Any

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

POSITIONS_RESPONSE: list[dict[str, Any]] = [
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfHeatPumps",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty heat pumps",
            "upperLimit": "4",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1,
        },
        "value": "1",
    },
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfHeatingCircuits",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty HC",
            "upperLimit": "8",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1,
        },
        "value": "1",
    },
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfHotWaterTanks",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty HW tank",
            "upperLimit": "4",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1,
        },
        "value": "1",
    },
]

DATA_RESPONSE: list[dict[str, Any]] = [
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.normalSetTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. Day",
            "unitId": "Temp",
            "upperLimit": "30",
            "lowerLimit": "10",
        },
        "value": "20.5",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.thresholdDayTemp.value",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Heating limit Day",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "-20",
        },
        "value": "20",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].values.heatRequest",
        "attributes": {
            "formatId": "fmtReqInfo",
            "longText": "Heat request",
            "unitId": "Enum",
            "upperLimit": "6",
            "lowerLimit": "0",
        },
        "value": "0",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holidaySetTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. Vacation",
            "unitId": "Temp",
            "upperLimit": "30",
            "lowerLimit": "10",
        },
        "value": "18",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.name",
        "attributes": {"longText": "Designation"},
        "value": "FBH",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.reducedSetTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. night",
            "unitId": "Temp",
            "upperLimit": "30",
            "lowerLimit": "10",
        },
        "value": "20",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.thresholdNightTemp.value",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Heat limit Night",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "-20",
        },
        "value": "18",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode",
        "attributes": {
            "formatId": "fmtHcMode",
            "longText": "Operating mode",
            "unitId": "Enum",
            "upperLimit": "32767",
            "lowerLimit": "0",
        },
        "value": "0",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].values.setValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. Nom.",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "10",
        },
        "value": "20.5",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Room temp. Offset",
            "unitId": "TempRel",
            "upperLimit": "2.5",
            "lowerLimit": "-2.5",
        },
        "value": "0",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].CircPump.values.setValueScaled",
        "attributes": {
            "formatId": "fmt3p0",
            "longText": "Circulation pump",
            "unitId": "Pct100",
            "upperLimit": "1",
            "lowerLimit": "0.0",
        },
        "value": "0",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].Compressor.values.setValueScaled",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Compressor",
            "unitId": "Pct100",
            "upperLimit": "1",
            "lowerLimit": "0.0",
        },
        "value": "0",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].TempCompressorIn.values.actValue",
        "attributes": {"formatId": "fmtTemp", "longText": "Comp. in temp.", "unitId": "Temp"},
        "value": "27.200001",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].TempCompressorOut.values.actValue",
        "attributes": {"formatId": "fmtTemp", "longText": "Comp. out temp.", "unitId": "Temp"},
        "value": "27.200001",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].values.request",
        "attributes": {"longText": "Heat pump request"},
        "value": "false",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].HighPressure.values.actValue",
        "attributes": {"formatId": "fmt3p2", "longText": "High pressure", "unitId": "PressBar"},
        "value": "15.61875",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].TempHeatFlow.values.actValue",
        "attributes": {"formatId": "fmtTemp", "longText": "Inflow temp.", "unitId": "Temp"},
        "value": "24.800001",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].LowPressure.values.actValue",
        "attributes": {"formatId": "fmt3p2", "longText": "Low pressure", "unitId": "PressBar"},
        "value": "15.354687",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].param.name",
        "attributes": {"longText": "Name"},
        "value": "WPS26",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].TempHeatReflux.values.actValue",
        "attributes": {"formatId": "fmtTemp", "longText": "Reflux temp.", "unitId": "Temp"},
        "value": "23.9",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].TempSourceIn.values.actValue",
        "attributes": {"formatId": "fmtTemp", "longText": "Source in temp.", "unitId": "Temp"},
        "value": "25.700001",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].TempSourceOut.values.actValue",
        "attributes": {"formatId": "fmtTemp", "longText": "Source out temp.", "unitId": "Temp"},
        "value": "24.9",
    },
    {
        "name": "APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState",
        "attributes": {
            "formatId": "fmtHPState",
            "longText": "State",
            "unitId": "Enum",
            "upperLimit": "32767",
            "lowerLimit": "0",
        },
        "value": "0",
    },
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[0].values.heatRequestTop",
        "attributes": {"longText": "Heat requirement"},
        "value": "false",
    },
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. nom.",
            "unitId": "Temp",
            "upperLimit": "52",
            "lowerLimit": "0",
            "dynUpperLimit": 1,
        },
        "value": "52",
    },
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.reducedSetTempMax.value",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Sup.temp.",
            "unitId": "Temp",
            "upperLimit": "52",
            "lowerLimit": "0",
            "dynUpperLimit": 1,
        },
        "value": "32.5",
    },
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode",
        "attributes": {
            "formatId": "fmtHotWaterTank",
            "longText": "Op.mode",
            "unitId": "Enum",
            "upperLimit": "32767",
            "lowerLimit": "0",
        },
        "value": "0",
    },
    {
        "name": "APPL.CtrlAppl.sParam.hotWaterTank[0].topTemp.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Temp. act.",
            "unitId": "Temp",
            "upperLimit": "90",
            "lowerLimit": "20",
        },
        "value": "47.700001",
    },
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfHeatingCircuits",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty HC",
            "upperLimit": "8",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1,
        },
        "value": "1",
    },
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfHeatPumps",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty heat pumps",
            "upperLimit": "4",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1,
        },
        "value": "1",
    },
    {
        "name": "APPL.CtrlAppl.sParam.options.systemNumberOfHotWaterTanks",
        "attributes": {
            "formatId": "fmt2p0",
            "longText": "Qty HW tank",
            "upperLimit": "4",
            "lowerLimit": "0",
            "dynLowerLimit": 1,
            "dynUpperLimit": 1,
        },
        "value": "1",
    },
    {
        "name": "APPL.CtrlAppl.sParam.outdoorTemp.values.actValue",
        "attributes": {
            "formatId": "fmtTemp",
            "longText": "Exterior temp.",
            "unitId": "Temp",
            "upperLimit": "100",
            "lowerLimit": "-100",
        },
        "value": "20.504164",
    },
]
