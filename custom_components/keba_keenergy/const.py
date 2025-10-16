"""Constants for the KEBA KeEnergy integration."""

from enum import Enum
from typing import Final
from typing import NamedTuple

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


class SupportedApiEndpoint(NamedTuple):
    """Minimal software version and section mapping."""

    section: Section
    min_version: str | None = None


SUPPORTED_API_ENDPOINTS: Final[dict[str, list[SupportedApiEndpoint]]] = {
    "ALL": [
        SupportedApiEndpoint(HeatCircuit.HAS_ROOM_TEMPERATURE),
        SupportedApiEndpoint(HeatCircuit.HAS_ROOM_HUMIDITY),
        SupportedApiEndpoint(HeatCircuit.ROOM_TEMPERATURE),
        SupportedApiEndpoint(HeatCircuit.ROOM_HUMIDITY),
        SupportedApiEndpoint(HeatCircuit.DEW_POINT),
        SupportedApiEndpoint(HeatCircuit.FLOW_TEMPERATURE_SETPOINT),
        SupportedApiEndpoint(HeatCircuit.FLOW_TEMPERATURE),
        SupportedApiEndpoint(HeatCircuit.RETURN_FLOW_TEMPERATURE),
        SupportedApiEndpoint(HeatCircuit.TARGET_TEMPERATURE_DAY),
        SupportedApiEndpoint(HeatCircuit.HEATING_LIMIT_DAY),
        SupportedApiEndpoint(HeatCircuit.HEAT_REQUEST),
        SupportedApiEndpoint(HeatCircuit.TARGET_TEMPERATURE_AWAY),
        SupportedApiEndpoint(HeatCircuit.NAME),
        SupportedApiEndpoint(HeatCircuit.TARGET_TEMPERATURE_NIGHT),
        SupportedApiEndpoint(HeatCircuit.HEATING_LIMIT_NIGHT),
        SupportedApiEndpoint(HeatCircuit.OPERATING_MODE),
        SupportedApiEndpoint(HeatCircuit.TARGET_TEMPERATURE),
        SupportedApiEndpoint(HeatCircuit.TARGET_TEMPERATURE_OFFSET),
        SupportedApiEndpoint(HeatPump.CIRCULATION_PUMP),
        SupportedApiEndpoint(HeatPump.COMPRESSOR),
        SupportedApiEndpoint(HeatPump.COMPRESSOR_INPUT_TEMPERATURE),
        SupportedApiEndpoint(HeatPump.COMPRESSOR_OUTPUT_TEMPERATURE),
        SupportedApiEndpoint(HeatPump.HEAT_REQUEST),
        SupportedApiEndpoint(HeatPump.HIGH_PRESSURE),
        SupportedApiEndpoint(HeatPump.FLOW_TEMPERATURE),
        SupportedApiEndpoint(HeatPump.LOW_PRESSURE),
        SupportedApiEndpoint(HeatPump.NAME),
        SupportedApiEndpoint(HeatPump.RETURN_FLOW_TEMPERATURE),
        SupportedApiEndpoint(HeatPump.SOURCE_INPUT_TEMPERATURE),
        SupportedApiEndpoint(HeatPump.SOURCE_OUTPUT_TEMPERATURE),
        SupportedApiEndpoint(HeatPump.STATE),
        SupportedApiEndpoint(HeatPump.COMPRESSOR_POWER),
        SupportedApiEndpoint(HeatPump.HEATING_POWER),
        SupportedApiEndpoint(HeatPump.HOT_WATER_POWER),
        SupportedApiEndpoint(HeatPump.COP),
        SupportedApiEndpoint(HeatPump.HEATING_ENERGY),
        SupportedApiEndpoint(HeatPump.HEATING_ENERGY_CONSUMPTION),
        SupportedApiEndpoint(HeatPump.HEATING_SPF),
        SupportedApiEndpoint(HeatPump.COOLING_ENERGY),
        SupportedApiEndpoint(HeatPump.COOLING_ENERGY_CONSUMPTION),
        SupportedApiEndpoint(HeatPump.COOLING_SPF),
        SupportedApiEndpoint(HeatPump.HOT_WATER_ENERGY),
        SupportedApiEndpoint(HeatPump.HOT_WATER_ENERGY_CONSUMPTION),
        SupportedApiEndpoint(HeatPump.HOT_WATER_SPF),
        SupportedApiEndpoint(HeatPump.TOTAL_THERMAL_ENERGY),
        SupportedApiEndpoint(HeatPump.TOTAL_ENERGY_CONSUMPTION),
        SupportedApiEndpoint(HeatPump.TOTAL_SPF),
        SupportedApiEndpoint(HeatPump.OPERATING_TIME),
        SupportedApiEndpoint(HeatPump.MAX_RUNTIME),
        SupportedApiEndpoint(HeatPump.ACTIVATION_COUNTER),
        SupportedApiEndpoint(HeatPump.HAS_PASSIVE_COOLING),
        SupportedApiEndpoint(HotWaterTank.HEAT_REQUEST),
        SupportedApiEndpoint(HotWaterTank.HOT_WATER_FLOW),
        SupportedApiEndpoint(HotWaterTank.FRESH_WATER_MODULE_TEMPERATURE),
        SupportedApiEndpoint(HotWaterTank.TARGET_TEMPERATURE),
        SupportedApiEndpoint(HotWaterTank.STANDBY_TEMPERATURE),
        SupportedApiEndpoint(HotWaterTank.OPERATING_MODE),
        SupportedApiEndpoint(HotWaterTank.CURRENT_TEMPERATURE),
        SupportedApiEndpoint(Photovoltaic.EXCESS_POWER),
        SupportedApiEndpoint(Photovoltaic.DAILY_ENERGY),
        SupportedApiEndpoint(Photovoltaic.TOTAL_ENERGY),
        SupportedApiEndpoint(System.HEAT_CIRCUIT_NUMBERS),
        SupportedApiEndpoint(System.HEAT_PUMP_NUMBERS),
        SupportedApiEndpoint(System.HOT_WATER_TANK_NUMBERS),
        SupportedApiEndpoint(System.EXTERNAL_HEAT_SOURCE_NUMBERS),
        SupportedApiEndpoint(System.OUTDOOR_TEMPERATURE),
        SupportedApiEndpoint(System.OPERATING_MODE),
        SupportedApiEndpoint(System.HAS_PHOTOVOLTAICS),
    ],
    SupportedDevice.AP_440.value: [
        SupportedApiEndpoint(ExternalHeatSource.OPERATING_MODE),
        SupportedApiEndpoint(ExternalHeatSource.TARGET_TEMPERATURE),
        SupportedApiEndpoint(ExternalHeatSource.HEAT_REQUEST),
        SupportedApiEndpoint(ExternalHeatSource.OPERATING_TIME),
        SupportedApiEndpoint(ExternalHeatSource.MAX_RUNTIME),
        SupportedApiEndpoint(ExternalHeatSource.ACTIVATION_COUNTER),
    ],
    SupportedDevice.AP_420.value: [
        SupportedApiEndpoint(ExternalHeatSource.OPERATING_MODE, min_version="4.02e"),
        SupportedApiEndpoint(ExternalHeatSource.TARGET_TEMPERATURE, min_version="4.02e"),
        SupportedApiEndpoint(ExternalHeatSource.HEAT_REQUEST, min_version="4.02e"),
        SupportedApiEndpoint(ExternalHeatSource.OPERATING_TIME, min_version="4.02e"),
        SupportedApiEndpoint(ExternalHeatSource.MAX_RUNTIME, min_version="4.02e"),
        SupportedApiEndpoint(ExternalHeatSource.ACTIVATION_COUNTER, min_version="4.02e"),
    ],
}
