# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Constants for the KEBA KeEnergy integration."""

from __future__ import annotations

from enum import Enum
from enum import StrEnum
from typing import TYPE_CHECKING
from typing import Final

import probatio
from homeassistant.components.climate.const import PRESET_AWAY
from homeassistant.components.climate.const import PRESET_BOOST
from homeassistant.components.climate.const import PRESET_COMFORT
from homeassistant.components.climate.const import PRESET_HOME
from homeassistant.components.climate.const import PRESET_SLEEP
from homeassistant.components.climate.const import HVACAction
from homeassistant.components.water_heater import STATE_ECO
from homeassistant.components.water_heater import STATE_HEAT_PUMP
from homeassistant.components.water_heater import STATE_PERFORMANCE
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_USERNAME
from homeassistant.const import STATE_OFF
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from keba_keenergy_api.constants import MAX_CURVE_TABLE_POINTS
from keba_keenergy_api.endpoints import ExternalHeatSource
from keba_keenergy_api.endpoints import HeatingCircuit
from keba_keenergy_api.endpoints import HeatPump
from keba_keenergy_api.endpoints import System
from keba_keenergy_api.enums import BufferTankOperatingMode
from keba_keenergy_api.enums import DeviceType
from keba_keenergy_api.enums import DHWTankOperatingMode
from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import HeatPumpState

if TYPE_CHECKING:
    from collections.abc import Mapping

    from keba_keenergy_api.endpoints import Endpoint


# TODO: Replace with the `DeviceType` of `keba_keenergy_api` and move to `legacy.py` as `LegacyDeviceType` when the
#  unique IDs, device identifiers and option keys are migrated to the `DeviceType` values.
class SectionPrefix(StrEnum):
    """Device types of the integration, part of the device identifiers and of the unique IDs."""

    SYSTEM = "system"
    BUFFER_TANK = "buffer_tank"
    HOT_WATER_TANK = "hot_water_tank"
    HEAT_PUMP = "heat_pump"
    HEAT_CIRCUIT = "heat_circuit"
    SOLAR_CIRCUIT = "solar_circuit"
    EXTERNAL_HEAT_SOURCE = "external_heat_source"
    SWITCH_VALVE = "switch_valve"
    PASSIVE_COOLING = "passive_cooling"
    PHOTOVOLTAICS = "photovoltaics"


class MixerPosition(Enum):
    """Positions of a mixer, derived from its setpoint (`-1..1`)."""

    CLOSED = -1
    OFF = 0
    OPEN = 1


ATTR_CONFIG_ENTRY: Final[str] = "config_entry"
ATTR_OFFSET: Final[str] = "offset"
ATTR_WRITES: Final[str] = "writes"
CONF_EXTERNAL_HEAT_SOURCE_TICK: Final[str] = "scan_interval_tick_external_heat_source"
CONF_BUFFER_TANK_TICK: Final[str] = "scan_interval_tick_buffer_tank"
CONF_HEAT_CIRCUIT_TICK: Final[str] = "scan_interval_tick_heat_circuit"
CONF_HEAT_PUMP_TICK: Final[str] = "scan_interval_tick_heat_pump"
CONF_HOT_WATER_TANK_TICK: Final[str] = "scan_interval_tick_hot_water_tank"
CONF_PHOTOVOLTAICS_TICK: Final[str] = "scan_interval_tick_photovoltaics"
CONF_SOLAR_CIRCUIT_TICK: Final[str] = "scan_interval_tick_solar_circuit"
CONF_SWITCH_VALVE_TICK: Final[str] = "scan_interval_tick_switch_valve"
CONF_SYSTEM_TICK: Final[str] = "scan_interval_tick_system"
CONFIG_ENTRY_VERSION: Final[int] = 1
DEFAULT_SCAN_INTERVAL: Final[int] = 20
DEFAULT_SSL: Final[bool] = False
DOMAIN: Final[str] = "keba_keenergy"
FLASH_WRITE_ISSUE_ID: Final[str] = "frequent_flash_writes"
FLASH_WRITE_LIMIT_PER_WEEK: Final[int] = 30
FLASH_WRITE_DELAY: Final[float] = 1
# Significant digits of a Float32, the Web HMI returns 8 digits (`0.8` as `0.80000001`).
FLOAT32_SIGNIFICANT_DIGITS: Final[int] = 7
MANUFACTURER: Final[str] = "KEBA"
MANUFACTURER_MTEC: Final[str] = "M-TEC"
MANUFACTURER_INO: Final[str] = "ino"
MIN_SCAN_INTERVAL: Final[int] = 20
NAME: Final[str] = "KeEnergy"
REQUEST_REFRESH_COOLDOWN: Final[float] = 0.5
SCAN_INTERVAL: Final[int] = 20

SERVICE_SET_AWAY_DATE_RANGE: Final[str] = "set_away_date_range"
SERVICE_SET_HEATING_CURVE_POINTS: Final[str] = "set_heating_curve_points"

PLATFORMS: Final[list[Platform]] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]

HEATING_CIRCUIT_PRESET_TO_HA: Final[Mapping[HeatingCircuitOperatingMode, str]] = {
    HeatingCircuitOperatingMode.AUTO: PRESET_HOME,
    HeatingCircuitOperatingMode.VACATION: PRESET_AWAY,
    HeatingCircuitOperatingMode.NORMAL: PRESET_COMFORT,
    HeatingCircuitOperatingMode.REDUCED: PRESET_SLEEP,
    HeatingCircuitOperatingMode.PARTY: PRESET_BOOST,
}

COOLING_CIRCUIT_PRESET_TO_HA: Final[Mapping[HeatingCircuitOperatingMode, str]] = {
    HeatingCircuitOperatingMode.AUTO: PRESET_HOME,
    HeatingCircuitOperatingMode.NORMAL: PRESET_COMFORT,
    HeatingCircuitOperatingMode.REDUCED: PRESET_SLEEP,
    HeatingCircuitOperatingMode.PARTY: PRESET_BOOST,
}

# The order is the priority with several heat pumps, e.g. one heat pump heats while another one defrosts.
# All other heat pump states are idle.
HEAT_PUMP_STATE_TO_HVAC_ACTION: Final[Mapping[HeatPumpState, HVACAction]] = {
    HeatPumpState.AUTOMATIC: HVACAction.HEATING,
    # The post-run still delivers heat while the compressor stops.
    HeatPumpState.POST_RUN: HVACAction.HEATING,
    HeatPumpState.DEFROST: HVACAction.DEFROSTING,
    # The pre-run starts the pumps, the compressor does not run yet.
    HeatPumpState.PRE_RUN: HVACAction.PREHEATING,
}

TEMPERATURE_OFFSET_SCHEMA: Final = {
    probatio.Required(ATTR_OFFSET, default=0): probatio.Coerce(float),
}

TEMPERATURE_SCHEMA: Final = {
    probatio.Required(ATTR_TEMPERATURE): probatio.Coerce(float),
}

STEP_AUTH_DATA_SCHEMA: Final[probatio.Schema] = probatio.Schema(
    {
        probatio.Required(CONF_USERNAME): str,
        probatio.Required(CONF_PASSWORD): str,
    },
)

# The configuration of the control unit per device type (e.g. the installed meters), read once on setup.
CONFIGURATION_ENDPOINTS: Final[Mapping[SectionPrefix, Mapping[str, Endpoint]]] = {
    SectionPrefix.SYSTEM: {
        "has_photovoltaics": System.HAS_PHOTOVOLTAICS,
    },
    SectionPrefix.HEAT_CIRCUIT: {
        "mode": HeatingCircuit.TYPE,
    },
    SectionPrefix.HOT_WATER_TANK: {},
    SectionPrefix.HEAT_PUMP: {
        "has_active_cooling": HeatPump.HAS_ACTIVE_COOLING,
        "has_passive_cooling": HeatPump.HAS_PASSIVE_COOLING,
        "electric_energy_meter_type": HeatPump.ELECTRICAL_ENERGY_METER_TYPE,
        "heat_meter_type": HeatPump.HEAT_METER_TYPE,
    },
    SectionPrefix.EXTERNAL_HEAT_SOURCE: {
        "has_emissions": ExternalHeatSource.HAS_EMISSIONS,
    },
}

# Passive cooling is a part of the heat pumps and uses their scan interval.
SCAN_INTERVAL_DEVICE_TYPES: Final[Mapping[SectionPrefix, SectionPrefix]] = {
    SectionPrefix.PASSIVE_COOLING: SectionPrefix.HEAT_PUMP,
}

# Device types of the API whose number of devices `get_device_counts()` returns, the others have no device number.
DEVICE_TYPES: Final[Mapping[SectionPrefix, DeviceType]] = {
    SectionPrefix.BUFFER_TANK: DeviceType.BUFFER_TANK,
    SectionPrefix.HOT_WATER_TANK: DeviceType.DHW_TANK,
    SectionPrefix.HEAT_PUMP: DeviceType.HEAT_PUMP,
    SectionPrefix.HEAT_CIRCUIT: DeviceType.HEATING_CIRCUIT,
    SectionPrefix.SOLAR_CIRCUIT: DeviceType.SOLAR_CIRCUIT,
    SectionPrefix.EXTERNAL_HEAT_SOURCE: DeviceType.EXTERNAL_HEAT_SOURCE,
    SectionPrefix.SWITCH_VALVE: DeviceType.SWITCH_VALVE,
    SectionPrefix.PASSIVE_COOLING: DeviceType.PASSIVE_COOLING,
}

# Keys of the heating and cooling curve in use, their sensors show the points of the curve.
CURVE_KEYS: Final[frozenset[str]] = frozenset({"cooling_curve", "heating_curve"})

TO_REDACT: Final[set[str]] = {
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    "serial_number",
    "title",
    "unique_id",
}

DEVICE_TRANSLATION_KEYS: Final[Mapping[SectionPrefix, str]] = {
    SectionPrefix.SYSTEM: "control_unit",
    SectionPrefix.HEAT_CIRCUIT: "heat_circuit",
    SectionPrefix.SOLAR_CIRCUIT: "solar_circuit",
    SectionPrefix.HEAT_PUMP: "heat_pump",
    SectionPrefix.BUFFER_TANK: "buffer_tank",
    SectionPrefix.HOT_WATER_TANK: "hot_water_tank",
    SectionPrefix.EXTERNAL_HEAT_SOURCE: "external_heat_source",
    SectionPrefix.SWITCH_VALVE: "switch_valve",
    SectionPrefix.PASSIVE_COOLING: "passive_cooling",
    SectionPrefix.PHOTOVOLTAICS: "photovoltaics",
}

HOT_WATER_TANK_STATE_TO_HA: Final[Mapping[DHWTankOperatingMode, str]] = {
    DHWTankOperatingMode.AUTO: STATE_ECO,
    DHWTankOperatingMode.MANUAL_CHARGE: STATE_PERFORMANCE,
    DHWTankOperatingMode.OFF: STATE_OFF,
    DHWTankOperatingMode.ON: STATE_HEAT_PUMP,
}

BUFFER_TANK_STATE_TO_HA: Final[Mapping[BufferTankOperatingMode, str]] = {
    BufferTankOperatingMode.MANUAL_CHARGE: STATE_PERFORMANCE,
    BufferTankOperatingMode.OFF: STATE_OFF,
    BufferTankOperatingMode.ON: STATE_HEAT_PUMP,
}

ATTR_START_DATE: Final[str] = "start_date"
ATTR_END_DATE: Final[str] = "end_date"

ATTR_POINTS: Final[str] = "points"
ATTR_OUTDOOR: Final[str] = "outdoor"
ATTR_FLOW: Final[str] = "flow"
ATTR_HEATING_CURVE: Final[str] = "heating_curve"

HEATING_CURVE_POINT_SCHEMA: Final = probatio.Schema(
    {
        probatio.Required(ATTR_OUTDOOR): probatio.All(
            probatio.Coerce(float),
            probatio.Range(min=-40, max=40),
        ),
        probatio.Required(ATTR_FLOW): probatio.All(
            probatio.Coerce(float),
            probatio.Range(min=10, max=90),
        ),
    },
)

HEATING_CURVE_POINTS_SCHEMA: Final[probatio.Schema] = probatio.Schema(
    {
        probatio.Required(ATTR_CONFIG_ENTRY): selector.ConfigEntrySelector(
            {
                "integration": DOMAIN,
            },
        ),
        probatio.Required(ATTR_HEATING_CURVE): probatio.All(
            str,
            probatio.Length(min=2),
            probatio.Match(r"^HC"),
        ),
        probatio.Required(ATTR_POINTS): probatio.All(
            cv.ensure_list,
            probatio.Length(min=1, max=MAX_CURVE_TABLE_POINTS),
            [HEATING_CURVE_POINT_SCHEMA],
        ),
    },
)
