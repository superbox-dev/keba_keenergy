# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Constants for the KEBA KeEnergy integration."""

from __future__ import annotations

from typing import Final

import probatio
from homeassistant.components.climate.const import PRESET_AWAY
from homeassistant.components.climate.const import PRESET_BOOST
from homeassistant.components.climate.const import PRESET_COMFORT
from homeassistant.components.climate.const import PRESET_HOME
from homeassistant.components.climate.const import PRESET_SLEEP
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
from keba_keenergy_api.constants import MAX_HEATING_CURVE_POINTS
from keba_keenergy_api.constants import BufferTank
from keba_keenergy_api.constants import BufferTankOperatingMode
from keba_keenergy_api.constants import ExternalHeatSource
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatCircuitOperatingMode
from keba_keenergy_api.constants import HeatPump
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import HotWaterTankOperatingMode
from keba_keenergy_api.constants import PassiveCooling
from keba_keenergy_api.constants import Photovoltaics
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import SolarCircuit
from keba_keenergy_api.constants import SwitchValve
from keba_keenergy_api.constants import System

ATTR_CONFIG_ENTRY: Final[str] = "config_entry"
ATTR_MESSAGE_ID: Final[str] = "message_id"
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

HEATING_CIRCUIT_PRESET_TO_HA: Final[dict[int, str]] = {
    HeatCircuitOperatingMode.AUTO.value: PRESET_HOME,
    HeatCircuitOperatingMode.HOLIDAY.value: PRESET_AWAY,
    HeatCircuitOperatingMode.DAY.value: PRESET_COMFORT,
    HeatCircuitOperatingMode.NIGHT.value: PRESET_SLEEP,
    HeatCircuitOperatingMode.PARTY.value: PRESET_BOOST,
}

COOLING_CIRCUIT_PRESET_TO_HA: Final[dict[int, str]] = {
    HeatCircuitOperatingMode.AUTO.value: PRESET_HOME,
    HeatCircuitOperatingMode.DAY.value: PRESET_COMFORT,
    HeatCircuitOperatingMode.NIGHT.value: PRESET_SLEEP,
    HeatCircuitOperatingMode.PARTY.value: PRESET_BOOST,
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

REQUEST_DATA_GROUPS: Final[dict[SectionPrefix, list[Section]]] = {
    SectionPrefix.EXTERNAL_HEAT_SOURCE: [
        ExternalHeatSource.OPERATING_MODE,
        ExternalHeatSource.TARGET_TEMPERATURE,
        ExternalHeatSource.HEAT_REQUEST,
        ExternalHeatSource.OPERATING_TIME,
        ExternalHeatSource.MAX_RUNTIME,
        ExternalHeatSource.ACTIVATION_COUNTER,
        ExternalHeatSource.USE_EXCESS_ENERGY,
        ExternalHeatSource.MIN_RUNTIME_EXCESS_ENERGY,
        ExternalHeatSource.CONSUMING_EXCESS_ENERGY,
        ExternalHeatSource.EXCESS_ENERGY_OPERATING_TIME,
        ExternalHeatSource.EXCESS_ENERGY_MAX_RUNTIME,
        ExternalHeatSource.EXCESS_ENERGY_ACTIVATION_COUNTER,
    ],
    SectionPrefix.HEAT_CIRCUIT: [
        HeatCircuit.ROOM_TEMPERATURE,
        HeatCircuit.ROOM_HUMIDITY,
        HeatCircuit.DEW_POINT,
        HeatCircuit.FLOW_TEMPERATURE_SETPOINT,
        HeatCircuit.MIXER_FLOW_TEMPERATURE,
        HeatCircuit.MIXER_RETURN_FLOW_TEMPERATURE,
        HeatCircuit.MIXER_POSITION,
        HeatCircuit.PUMP_STATE,
        HeatCircuit.RETURN_FLOW_TEMPERATURE,
        HeatCircuit.TARGET_TEMPERATURE_DAY,
        HeatCircuit.TARGET_COOLING_TEMPERATURE_DAY,
        HeatCircuit.HEATING_LIMIT_DAY,
        HeatCircuit.COOLING_LIMIT_DAY,
        HeatCircuit.EXCESS_ENERGY_HEATING_LIMIT_DAY,
        HeatCircuit.EXCESS_ENERGY_COOLING_LIMIT_DAY,
        HeatCircuit.HEAT_REQUEST,
        HeatCircuit.COOL_REQUEST,
        HeatCircuit.TARGET_TEMPERATURE_AWAY,
        HeatCircuit.TARGET_TEMPERATURE_NIGHT,
        HeatCircuit.TARGET_COOLING_TEMPERATURE_NIGHT,
        HeatCircuit.HEATING_LIMIT_NIGHT,
        HeatCircuit.COOLING_LIMIT_NIGHT,
        HeatCircuit.EXCESS_ENERGY_HEATING_LIMIT_NIGHT,
        HeatCircuit.EXCESS_ENERGY_COOLING_LIMIT_NIGHT,
        HeatCircuit.OPERATING_MODE,
        HeatCircuit.SELECTED_TARGET_TEMPERATURE,
        HeatCircuit.TARGET_TEMPERATURE,
        HeatCircuit.TARGET_TEMPERATURE_OFFSET,
        HeatCircuit.USE_EXCESS_ENERGY,
        HeatCircuit.EXCESS_ENERGY_TARGET_TEMPERATURE,
        HeatCircuit.EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS,
        HeatCircuit.EXCESS_ENERGY_TARGET_COOLING_TEMPERATURE,
        HeatCircuit.EXCESS_ENERGY_TARGET_COOLING_TEMPERATURE_HYSTERESIS,
        HeatCircuit.EXCESS_ENERGY_MODE,
        HeatCircuit.AWAY_START_DATE,
        HeatCircuit.AWAY_END_DATE,
        HeatCircuit.HEATING_CURVE_OFFSET,
        HeatCircuit.COOLING_CURVE_OFFSET,
        HeatCircuit.HEATING_CURVE_SLOPE,
        HeatCircuit.COOLING_CURVE_SLOPE,
        HeatCircuit.USE_HEATING_CURVE,
        HeatCircuit.HEATING_CURVE,
        HeatCircuit.COOLING_CURVE,
        HeatCircuit.PUMP_SPEED,
    ],
    SectionPrefix.SOLAR_CIRCUIT: [
        SolarCircuit.OPERATING_MODE,
        SolarCircuit.SOURCE_TEMPERATURE,
        SolarCircuit.PUMP_1,
        SolarCircuit.PUMP_2,
        SolarCircuit.CURRENT_TEMPERATURE,
        SolarCircuit.TARGET_TEMPERATURE,
        SolarCircuit.HEAT_REQUEST,
        SolarCircuit.HEATING_ENERGY,
        SolarCircuit.DAILY_ENERGY,
        SolarCircuit.ACTUAL_POWER,
        SolarCircuit.PRIORITY_1_BEFORE_2,
    ],
    SectionPrefix.HEAT_PUMP: [
        HeatPump.CONSUMING_EXCESS_ENERGY,
        HeatPump.EXCESS_ENERGY_OPERATING_TIME,
        HeatPump.EXCESS_ENERGY_MAX_RUNTIME,
        HeatPump.EXCESS_ENERGY_ACTIVATION_COUNTER,
        HeatPump.CIRCULATION_PUMP_SPEED,
        HeatPump.SOURCE_PUMP_SPEED,
        HeatPump.COMPRESSOR,
        HeatPump.COMPRESSOR_NIGHT_SPEED,
        HeatPump.COMPRESSOR_INPUT_TEMPERATURE,
        HeatPump.COMPRESSOR_OUTPUT_TEMPERATURE,
        HeatPump.COMPRESSOR_USE_NIGHT_SPEED,
        HeatPump.CONDENSER_TEMPERATURE,
        HeatPump.VAPORIZER_TEMPERATURE,
        HeatPump.TARGET_OVERHEATING,
        HeatPump.CURRENT_OVERHEATING,
        HeatPump.EXPANSION_VALVE_POSITION,
        HeatPump.HEAT_REQUEST,
        HeatPump.HIGH_PRESSURE,
        HeatPump.FLOW_TEMPERATURE,
        HeatPump.LOW_PRESSURE,
        HeatPump.NAME,
        HeatPump.RETURN_FLOW_TEMPERATURE,
        HeatPump.SOURCE_INPUT_TEMPERATURE,
        HeatPump.SOURCE_OUTPUT_TEMPERATURE,
        HeatPump.STATE,
        HeatPump.SUBSTATE,
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
        HeatPump.EXCESS_ENERGY_CONSUMPTION,
        HeatPump.HEATING_EXCESS_ENERGY_CONSUMPTION,
        HeatPump.COOLING_EXCESS_ENERGY_CONSUMPTION,
        HeatPump.HOT_WATER_EXCESS_ENERGY_CONSUMPTION,
        HeatPump.OPERATING_TIME,
        HeatPump.MAX_RUNTIME,
        HeatPump.ACTIVATION_COUNTER,
        HeatPump.HAS_COMPRESSOR_FAILURE,
        HeatPump.HAS_SOURCE_FAILURE,
        HeatPump.HAS_SOURCE_ACTUATOR_FAILURE,
        HeatPump.HAS_THREE_PHASE_FAILURE,
        HeatPump.HAS_SOURCE_PRESSURE_FAILURE,
        HeatPump.HAS_VFD_FAILURE,
        # Passive cooling has no own group for the ticks, it is always a part of the heat pumps.
        PassiveCooling.TEMPERATURE,
        PassiveCooling.SWITCH_VALVE_POSITION,
        PassiveCooling.CIRCULATION_PUMP_SPEED,
        PassiveCooling.MIXER_FLOW_TEMPERATURE,
        PassiveCooling.MIXER_TARGET_TEMPERATURE,
        PassiveCooling.MIXER_POSITION,
    ],
    SectionPrefix.BUFFER_TANK: [
        BufferTank.CURRENT_TOP_TEMPERATURE,
        BufferTank.CURRENT_BOTTOM_TEMPERATURE,
        BufferTank.EXCESS_ENERGY_TARGET_TEMPERATURE,
        BufferTank.EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS,
        BufferTank.EXCESS_ENERGY_MODE,
        BufferTank.OPERATING_MODE,
        BufferTank.STANDBY_TEMPERATURE,
        BufferTank.TARGET_TEMPERATURE,
        BufferTank.HEAT_REQUEST,
        BufferTank.COOL_REQUEST,
        BufferTank.USE_EXCESS_ENERGY,
        BufferTank.OUTDOOR_TEMPERATURE_EXCESS_ENERGY_LIMIT,
    ],
    SectionPrefix.HOT_WATER_TANK: [
        HotWaterTank.USE_EXCESS_ENERGY,
        HotWaterTank.EXCESS_ENERGY_TARGET_TEMPERATURE,
        HotWaterTank.EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS,
        HotWaterTank.EXCESS_ENERGY_MODE,
        HotWaterTank.HEAT_REQUEST,
        HotWaterTank.FRESH_WATER_FLOW,
        HotWaterTank.FRESH_WATER_MODULE_TEMPERATURE,
        HotWaterTank.TARGET_TEMPERATURE,
        HotWaterTank.STANDBY_TEMPERATURE,
        HotWaterTank.OPERATING_MODE,
        HotWaterTank.CURRENT_TEMPERATURE,
        HotWaterTank.CIRCULATION_RETURN_TEMPERATURE,
        HotWaterTank.CIRCULATION_PUMP_STATE,
    ],
    SectionPrefix.SWITCH_VALVE: [
        SwitchValve.POSITION,
    ],
    SectionPrefix.PHOTOVOLTAICS: [
        Photovoltaics.EXCESS_ENERGY_ACTIVE,
        Photovoltaics.EXCESS_POWER,
        Photovoltaics.DAILY_ENERGY,
        Photovoltaics.TOTAL_ENERGY,
    ],
    SectionPrefix.SYSTEM: [
        System.OUTDOOR_TEMPERATURE,
        System.OPERATING_MODE,
        System.CPU_USAGE,
        System.WEBVIEW_CPU_USAGE,
        System.WEBSERVER_CPU_USAGE,
        System.CONTROL_CPU_USAGE,
        System.RAM_USAGE,
        System.FREE_RAM,
        System.FLASH_ERASE_COUNTER,
    ],
}

TO_REDACT: Final[set[str]] = {
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    "serial_number",
    "title",
    "unique_id",
}

DEVICE_TRANSLATION_KEYS: Final[dict[str, str]] = {
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

SECTIONS: Final[dict[str, type[Section]]] = {
    SectionPrefix.SYSTEM: System,
    SectionPrefix.HEAT_CIRCUIT: HeatCircuit,
    SectionPrefix.SOLAR_CIRCUIT: SolarCircuit,
    SectionPrefix.HEAT_PUMP: HeatPump,
    SectionPrefix.BUFFER_TANK: BufferTank,
    SectionPrefix.HOT_WATER_TANK: HotWaterTank,
    SectionPrefix.EXTERNAL_HEAT_SOURCE: ExternalHeatSource,
}

SECTION_PREFIXES: Final[dict[type[Section], str]] = {section: prefix for prefix, section in SECTIONS.items()}

HOT_WATER_TANK_STATE_TO_HA: Final[dict[int, str]] = {
    HotWaterTankOperatingMode.AUTO.value: STATE_ECO,
    HotWaterTankOperatingMode.HEAT_UP.value: STATE_PERFORMANCE,
    HotWaterTankOperatingMode.OFF.value: STATE_OFF,
    HotWaterTankOperatingMode.ON.value: STATE_HEAT_PUMP,
}

BUFFER_TANK_STATE_TO_HA: Final[dict[int, str]] = {
    BufferTankOperatingMode.HEAT_UP.value: STATE_PERFORMANCE,
    BufferTankOperatingMode.OFF.value: STATE_OFF,
    BufferTankOperatingMode.ON.value: STATE_HEAT_PUMP,
}

HOT_WATER_TANK_OPERATING_MODE_TO_HA: Final[dict[str, str]] = {
    HotWaterTankOperatingMode(key).name.lower(): value for key, value in HOT_WATER_TANK_STATE_TO_HA.items()
}

BUFFER_TANK_OPERATING_MODE_TO_HA: Final[dict[str, str]] = {
    BufferTankOperatingMode(key).name.lower(): value for key, value in BUFFER_TANK_STATE_TO_HA.items()
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
            probatio.Length(min=1, max=MAX_HEATING_CURVE_POINTS),
            [HEATING_CURVE_POINT_SCHEMA],
        ),
    },
)
