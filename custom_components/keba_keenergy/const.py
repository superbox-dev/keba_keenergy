"""Constants for the KEBA KeEnergy integration."""

from enum import Enum
from typing import Final

from keba_keenergy_api.constants import ExternalHeatSource
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatPump
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import Photovoltaic
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import System

ATTR_OFFSET: Final[str] = "offset"
CONFIG_ENTRY_VERSION: Final[int] = 1
DEFAULT_SSL: Final[bool] = False
DOMAIN: Final[str] = "keba_keenergy"
MANUFACTURER: Final = "KEBA"
MANUFACTURER_MTEC: Final = "M-TEC"
MANUFACTURER_INO: Final = "ino"
NAME: Final = "KeEnergy"
SCAN_INTERVAL: Final[int] = 20


class SupportedDevice(Enum):
    """A list of supported devices."""

    AP_420 = "AP 420/H-A"
    AP_440 = "AP 440/H-A"


SUPPORTED_API_ENDPOINTS: Final[dict[str, list[Section]]] = {
    "ALL": [
        HeatCircuit.HAS_ROOM_TEMPERATURE,
        HeatCircuit.HAS_ROOM_HUMIDITY,
        HeatCircuit.ROOM_TEMPERATURE,
        HeatCircuit.ROOM_HUMIDITY,
        HeatCircuit.DEW_POINT,
        HeatCircuit.FLOW_TEMPERATURE_SETPOINT,
        HeatCircuit.FLOW_TEMPERATURE,
        HeatCircuit.RETURN_FLOW_TEMPERATURE,
        HeatCircuit.TARGET_TEMPERATURE_DAY,
        HeatCircuit.HEATING_LIMIT_DAY,
        HeatCircuit.HEAT_REQUEST,
        HeatCircuit.TARGET_TEMPERATURE_AWAY,
        HeatCircuit.NAME,
        HeatCircuit.TARGET_TEMPERATURE_NIGHT,
        HeatCircuit.HEATING_LIMIT_NIGHT,
        HeatCircuit.OPERATING_MODE,
        HeatCircuit.TARGET_TEMPERATURE,
        HeatCircuit.TARGET_TEMPERATURE_OFFSET,
        HeatPump.CIRCULATION_PUMP,
        HeatPump.COMPRESSOR,
        HeatPump.COMPRESSOR_INPUT_TEMPERATURE,
        HeatPump.COMPRESSOR_OUTPUT_TEMPERATURE,
        HeatPump.HEAT_REQUEST,
        HeatPump.HIGH_PRESSURE,
        HeatPump.FLOW_TEMPERATURE,
        HeatPump.LOW_PRESSURE,
        HeatPump.NAME,
        HeatPump.RETURN_FLOW_TEMPERATURE,
        HeatPump.SOURCE_INPUT_TEMPERATURE,
        HeatPump.SOURCE_OUTPUT_TEMPERATURE,
        HeatPump.STATE,
        HeatPump.COMPRESSOR_POWER,
        HeatPump.HEATING_POWER,
        HeatPump.HOT_WATER_POWER,
        HeatPump.COP,
        HeatPump.HEATING_ENERGY,
        HeatPump.HEATING_ENERGY_CONSUMPTION,
        HeatPump.HEATING_SPF,
        HeatPump.COOLING_ENERGY,
        HeatPump.COOLING_ENERGY_CONSUMPTION,
        HeatPump.COOLING_SPF,
        HeatPump.HOT_WATER_ENERGY,
        HeatPump.HOT_WATER_ENERGY_CONSUMPTION,
        HeatPump.HOT_WATER_SPF,
        HeatPump.TOTAL_THERMAL_ENERGY,
        HeatPump.TOTAL_ENERGY_CONSUMPTION,
        HeatPump.TOTAL_SPF,
        HeatPump.OPERATING_TIME,
        HeatPump.MAX_RUNTIME,
        HeatPump.ACTIVATION_COUNTER,
        HeatPump.HAS_PASSIVE_COOLING,
        HotWaterTank.HEAT_REQUEST,
        HotWaterTank.HOT_WATER_FLOW,
        HotWaterTank.FRESH_WATER_MODULE_TEMPERATURE,
        HotWaterTank.TARGET_TEMPERATURE,
        HotWaterTank.STANDBY_TEMPERATURE,
        HotWaterTank.OPERATING_MODE,
        HotWaterTank.CURRENT_TEMPERATURE,
        Photovoltaic.EXCESS_POWER,
        Photovoltaic.DAILY_ENERGY,
        Photovoltaic.TOTAL_ENERGY,
        System.HEAT_CIRCUIT_NUMBERS,
        System.HEAT_PUMP_NUMBERS,
        System.HOT_WATER_TANK_NUMBERS,
        System.EXTERNAL_HEAT_SOURCE_NUMBERS,
        System.OUTDOOR_TEMPERATURE,
        System.OPERATING_MODE,
        System.HAS_PHOTOVOLTAICS,
    ],
    SupportedDevice.AP_440.value: [
        ExternalHeatSource.OPERATING_MODE,
        ExternalHeatSource.TARGET_TEMPERATURE,
        ExternalHeatSource.HEAT_REQUEST,
        ExternalHeatSource.OPERATING_TIME,
        ExternalHeatSource.MAX_RUNTIME,
        ExternalHeatSource.ACTIVATION_COUNTER,
    ],
}
