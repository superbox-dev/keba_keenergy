# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Compatibility with `keba_keenergy_api` 2.x for the KEBA KeEnergy integration.

The entities keep the keys and states of `keba_keenergy_api` 2.x, so that unique IDs, entity IDs and states of existing
installations do not change.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final
from typing import Protocol

from keba_keenergy_api.endpoints import BufferTank
from keba_keenergy_api.endpoints import DHWTank
from keba_keenergy_api.endpoints import ExternalHeatSource
from keba_keenergy_api.endpoints import HeatingCircuit
from keba_keenergy_api.endpoints import HeatPump
from keba_keenergy_api.endpoints import PassiveCooling
from keba_keenergy_api.endpoints import Photovoltaics
from keba_keenergy_api.endpoints import SolarCircuit
from keba_keenergy_api.endpoints import SwitchValve
from keba_keenergy_api.endpoints import System
from keba_keenergy_api.enums import BufferTankOperatingMode
from keba_keenergy_api.enums import DHWTankOperatingMode
from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import HeatingCircuitRequest
from keba_keenergy_api.enums import HeatPumpState
from keba_keenergy_api.enums import HeatPumpSubState
from keba_keenergy_api.enums import SwitchValvePosition
from keba_keenergy_api.enums import SystemOperatingMode

from .const import SectionPrefix

if TYPE_CHECKING:
    from collections.abc import Mapping
    from enum import Enum

    from keba_keenergy_api.endpoints import Endpoint

# States of the entities that kept the names of the enum members of `keba_keenergy_api` 2.x, the states of all other
# members are their lowercase names.
LEGACY_STATES: Final[Mapping[Enum, str]] = {
    BufferTankOperatingMode.MANUAL_CHARGE: "heat_up",
    DHWTankOperatingMode.MANUAL_CHARGE: "heat_up",
    HeatingCircuitOperatingMode.NORMAL: "day",
    HeatingCircuitOperatingMode.REDUCED: "night",
    HeatingCircuitOperatingMode.VACATION: "holiday",
    HeatingCircuitRequest.ACTIVE: "on",
    HeatingCircuitRequest.FLOW_OFF: "inflow_off",
    HeatingCircuitRequest.RETURN_OFF: "flow_off",
    HeatingCircuitRequest.TEMPERATURE_PRIORITY_OFF: "temporary_off",
    HeatPumpState.AUTOMATIC: "auto_heat",
    HeatPumpState.COOLING: "auto_cool",
    HeatPumpState.POST_RUN: "inflow",
    HeatPumpState.PRE_RUN: "flow",
    HeatPumpSubState.DEFROST_FAN: "defrost_venting",
    HeatPumpSubState.DEFROST_PRE_RUN: "defrost_pre_flow",
    HeatPumpSubState.OPENING: "open",
    HeatPumpSubState.PRE_RUN_HEAT_UP: "preheat_flow",
    HeatPumpSubState.RETURN_OFF: "return_flow_off",
    HeatPumpSubState.SWITCHING_HEATING_COOLING: "switch_heating_cooling",
    HeatPumpSubState.WAITING_FOR_COMPRESSOR: "wait_for_compressor",
    SwitchValvePosition.POSITION_1: "open",
    SwitchValvePosition.POSITION_2: "closed",
    SystemOperatingMode.AUTO_COOLING: "auto_cool",
    SystemOperatingMode.AUTO_HEATING: "auto_heat",
}

# The polled values per device type, by the key of the coordinator data (the name of the value in
# `keba_keenergy_api` 2.x, also part of the unique IDs).
ENDPOINTS: Final[Mapping[SectionPrefix, Mapping[str, Endpoint]]] = {
    SectionPrefix.EXTERNAL_HEAT_SOURCE: {
        "operating_mode": ExternalHeatSource.OPERATING_MODE,
        "target_temperature": ExternalHeatSource.TARGET_TEMPERATURE,
        "heat_request": ExternalHeatSource.HEATING_REQUEST,
        "operating_time": ExternalHeatSource.OPERATING_TIME,
        "max_runtime": ExternalHeatSource.MAX_RUNTIME,
        "activation_counter": ExternalHeatSource.ACTIVATION_COUNTER,
        "use_excess_energy": ExternalHeatSource.USE_EXCESS_ENERGY,
        "min_runtime_excess_energy": ExternalHeatSource.EXCESS_ENERGY_MIN_RUNTIME,
        "consuming_excess_energy": ExternalHeatSource.EXCESS_ENERGY_ACTIVE,
        "excess_energy_operating_time": ExternalHeatSource.EXCESS_ENERGY_OPERATING_TIME,
        "excess_energy_max_runtime": ExternalHeatSource.EXCESS_ENERGY_MAX_RUNTIME,
        "excess_energy_activation_counter": ExternalHeatSource.EXCESS_ENERGY_ACTIVATION_COUNTER,
    },
    SectionPrefix.HEATING_CIRCUIT: {
        "room_temperature": HeatingCircuit.ROOM_TEMPERATURE,
        "room_humidity": HeatingCircuit.ROOM_HUMIDITY,
        "dew_point": HeatingCircuit.DEW_POINT,
        "flow_temperature_setpoint": HeatingCircuit.TARGET_FLOW_TEMPERATURE,
        "mixer_flow_temperature": HeatingCircuit.MIXER_FLOW_TEMPERATURE,
        "mixer_return_flow_temperature": HeatingCircuit.MIXER_RETURN_TEMPERATURE,
        "mixer_position": HeatingCircuit.MIXER_SETPOINT,
        "pump_state": HeatingCircuit.PUMP_ACTIVE,
        "return_flow_temperature": HeatingCircuit.RETURN_TEMPERATURE,
        "target_temperature_day": HeatingCircuit.TARGET_ROOM_TEMPERATURE_NORMAL,
        "target_cooling_temperature_day": HeatingCircuit.TARGET_ROOM_COOLING_TEMPERATURE_NORMAL,
        "heating_limit_day": HeatingCircuit.HEATING_LIMIT_NORMAL,
        "cooling_limit_day": HeatingCircuit.COOLING_LIMIT_NORMAL,
        "excess_energy_heating_limit_day": HeatingCircuit.EXCESS_ENERGY_HEATING_LIMIT_NORMAL,
        "excess_energy_cooling_limit_day": HeatingCircuit.EXCESS_ENERGY_COOLING_LIMIT_NORMAL,
        "heat_request": HeatingCircuit.HEATING_REQUEST,
        "cool_request": HeatingCircuit.COOLING_REQUEST,
        "target_temperature_away": HeatingCircuit.TARGET_ROOM_TEMPERATURE_VACATION,
        "target_temperature_night": HeatingCircuit.TARGET_ROOM_TEMPERATURE_REDUCED,
        "target_cooling_temperature_night": HeatingCircuit.TARGET_ROOM_COOLING_TEMPERATURE_REDUCED,
        "heating_limit_night": HeatingCircuit.HEATING_LIMIT_REDUCED,
        "cooling_limit_night": HeatingCircuit.COOLING_LIMIT_REDUCED,
        "excess_energy_heating_limit_night": HeatingCircuit.EXCESS_ENERGY_HEATING_LIMIT_REDUCED,
        "excess_energy_cooling_limit_night": HeatingCircuit.EXCESS_ENERGY_COOLING_LIMIT_REDUCED,
        "operating_mode": HeatingCircuit.OPERATING_MODE,
        "selected_target_temperature": HeatingCircuit.SELECTED_TARGET_ROOM_TEMPERATURE,
        "target_temperature": HeatingCircuit.TARGET_ROOM_TEMPERATURE,
        "target_temperature_offset": HeatingCircuit.ROOM_TEMPERATURE_OFFSET,
        "use_excess_energy": HeatingCircuit.USE_EXCESS_ENERGY,
        "excess_energy_target_temperature": HeatingCircuit.EXCESS_ENERGY_TARGET_ROOM_TEMPERATURE,
        "excess_energy_target_temperature_hysteresis": HeatingCircuit.EXCESS_ENERGY_TARGET_ROOM_TEMPERATURE_HYSTERESIS,
        "excess_energy_target_cooling_temperature": HeatingCircuit.EXCESS_ENERGY_TARGET_ROOM_COOLING_TEMPERATURE,
        "excess_energy_target_cooling_temperature_hysteresis": (
            HeatingCircuit.EXCESS_ENERGY_TARGET_ROOM_COOLING_TEMPERATURE_HYSTERESIS
        ),
        "excess_energy_mode": HeatingCircuit.EXCESS_ENERGY_STATE,
        "away_start_date": HeatingCircuit.VACATION_START,
        "away_end_date": HeatingCircuit.VACATION_END,
        "heating_curve_offset": HeatingCircuit.HEATING_CURVE_OFFSET,
        "cooling_curve_offset": HeatingCircuit.COOLING_CURVE_OFFSET,
        "heating_curve_slope": HeatingCircuit.HEATING_CURVE_SLOPE,
        "cooling_curve_slope": HeatingCircuit.COOLING_CURVE_SLOPE,
        "use_heating_curve": HeatingCircuit.USE_CURVE_TABLE,
        "heating_curve": HeatingCircuit.HEATING_CURVE,
        "cooling_curve": HeatingCircuit.COOLING_CURVE,
        "pump_speed": HeatingCircuit.PUMP_SPEED,
    },
    SectionPrefix.SOLAR_CIRCUIT: {
        "operating_mode": SolarCircuit.OPERATING_MODE,
        "source_temperature": SolarCircuit.COLLECTOR_TEMPERATURE,
        "pump_1": SolarCircuit.PUMP_1_SPEED,
        "pump_2": SolarCircuit.PUMP_2_SPEED,
        "current_temperature": SolarCircuit.CONSUMER_TEMPERATURE,
        "target_temperature": SolarCircuit.CONSUMER_TARGET_TEMPERATURE,
        "heat_request": SolarCircuit.CONSUMER_HEATING_REQUEST,
        "heating_energy": SolarCircuit.METER_ACCUMULATED_THERMAL_ENERGY,
        "daily_energy": SolarCircuit.METER_DAILY_THERMAL_ENERGY,
        "actual_power": SolarCircuit.METER_THERMAL_POWER,
        "priority_1_before_2": SolarCircuit.CONSUMER_1_PRIORITY,
    },
    SectionPrefix.HEAT_PUMP: {
        "consuming_excess_energy": HeatPump.EXCESS_ENERGY_ACTIVE,
        "excess_energy_operating_time": HeatPump.EXCESS_ENERGY_OPERATING_TIME,
        "excess_energy_max_runtime": HeatPump.EXCESS_ENERGY_MAX_RUNTIME,
        "excess_energy_activation_counter": HeatPump.EXCESS_ENERGY_ACTIVATION_COUNTER,
        "circulation_pump_speed": HeatPump.CIRCULATION_PUMP_SPEED,
        "source_pump_speed": HeatPump.SOURCE_ACTUATOR_SPEED,
        "compressor": HeatPump.COMPRESSOR_SPEED,
        "compressor_night_speed": HeatPump.COMPRESSOR_NIGHT_POWER_LIMIT,
        "compressor_input_temperature": HeatPump.COMPRESSOR_INLET_TEMPERATURE,
        "compressor_output_temperature": HeatPump.COMPRESSOR_OUTLET_TEMPERATURE,
        "compressor_use_night_speed": HeatPump.USE_COMPRESSOR_NIGHT_POWER_LIMIT,
        "condenser_temperature": HeatPump.CONDENSATION_TEMPERATURE,
        "vaporizer_temperature": HeatPump.EVAPORATION_TEMPERATURE,
        "target_overheating": HeatPump.TARGET_SUCTION_SUPERHEAT,
        "current_overheating": HeatPump.SUCTION_SUPERHEAT,
        "expansion_valve_position": HeatPump.EXPANSION_VALVE_POSITION,
        "heat_request": HeatPump.REQUEST,
        "high_pressure": HeatPump.HIGH_PRESSURE,
        "flow_temperature": HeatPump.FLOW_TEMPERATURE,
        "low_pressure": HeatPump.LOW_PRESSURE,
        "name": HeatPump.NAME,
        "return_flow_temperature": HeatPump.RETURN_TEMPERATURE,
        "source_input_temperature": HeatPump.SOURCE_INLET_TEMPERATURE,
        "source_output_temperature": HeatPump.SOURCE_OUTLET_TEMPERATURE,
        "state": HeatPump.STATE,
        "substate": HeatPump.SUB_STATE,
        "compressor_power": HeatPump.METER_ELECTRICAL_POWER,
        "heating_power": HeatPump.HEATING_METER_THERMAL_POWER,
        "hot_water_power": HeatPump.DHW_METER_THERMAL_POWER,
        "cop": HeatPump.COP,
        "heating_energy": HeatPump.HEATING_THERMAL_ENERGY,
        "heating_energy_consumption": HeatPump.HEATING_ELECTRICAL_ENERGY,
        "heating_spf": HeatPump.HEATING_SPF,
        "cooling_energy": HeatPump.COOLING_THERMAL_ENERGY,
        "cooling_energy_consumption": HeatPump.COOLING_ELECTRICAL_ENERGY,
        "cooling_spf": HeatPump.COOLING_SPF,
        "hot_water_energy": HeatPump.DHW_THERMAL_ENERGY,
        "hot_water_energy_consumption": HeatPump.DHW_ELECTRICAL_ENERGY,
        "hot_water_spf": HeatPump.DHW_SPF,
        "total_thermal_energy": HeatPump.TOTAL_THERMAL_ENERGY,
        "total_energy_consumption": HeatPump.TOTAL_ELECTRICAL_ENERGY,
        "total_spf": HeatPump.TOTAL_SPF,
        "excess_energy_consumption": HeatPump.EXCESS_ENERGY_CONSUMPTION,
        "heating_excess_energy_consumption": HeatPump.EXCESS_ENERGY_HEATING_CONSUMPTION,
        "cooling_excess_energy_consumption": HeatPump.EXCESS_ENERGY_COOLING_CONSUMPTION,
        "hot_water_excess_energy_consumption": HeatPump.EXCESS_ENERGY_DHW_CONSUMPTION,
        "operating_time": HeatPump.OPERATING_TIME,
        "max_runtime": HeatPump.MAX_RUNTIME,
        "activation_counter": HeatPump.ACTIVATION_COUNTER,
        "has_compressor_failure": HeatPump.COMPRESSOR_FAILURE,
        "has_source_failure": HeatPump.SOURCE_FAILURE,
        "has_source_actuator_failure": HeatPump.SOURCE_ACTUATOR_FAILURE,
        "has_three_phase_failure": HeatPump.THREE_PHASE_FAILURE,
        "has_source_pressure_failure": HeatPump.SOURCE_PRESSURE_FAILURE,
        "has_vfd_failure": HeatPump.VFD_FAILURE,
    },
    SectionPrefix.PASSIVE_COOLING: {
        "temperature": PassiveCooling.TEMPERATURE,
        "switch_valve_position": PassiveCooling.SWITCH_VALVE_POSITION,
        "circulation_pump_speed": PassiveCooling.CIRCULATION_PUMP_SPEED,
        "mixer_flow_temperature": PassiveCooling.MIXER_FLOW_TEMPERATURE,
        "mixer_target_temperature": PassiveCooling.MIXER_TARGET_TEMPERATURE,
        "mixer_position": PassiveCooling.MIXER_SETPOINT,
    },
    SectionPrefix.BUFFER_TANK: {
        "current_top_temperature": BufferTank.TOP_TEMPERATURE,
        "current_bottom_temperature": BufferTank.BOTTOM_TEMPERATURE,
        "excess_energy_target_temperature": BufferTank.EXCESS_ENERGY_TARGET_TEMPERATURE,
        "excess_energy_target_temperature_hysteresis": BufferTank.EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS,
        "excess_energy_mode": BufferTank.EXCESS_ENERGY_STATE,
        "operating_mode": BufferTank.OPERATING_MODE,
        "standby_temperature": BufferTank.BACKUP_TEMPERATURE,
        "target_temperature": BufferTank.TARGET_TEMPERATURE,
        "heat_request": BufferTank.HEATING_REQUEST,
        "cool_request": BufferTank.COOLING_REQUEST,
        "use_excess_energy": BufferTank.USE_EXCESS_ENERGY,
        "outdoor_temperature_excess_energy_limit": BufferTank.EXCESS_ENERGY_OUTDOOR_TEMPERATURE_LIMIT,
    },
    SectionPrefix.DHW_TANK: {
        "use_excess_energy": DHWTank.USE_EXCESS_ENERGY,
        "excess_energy_target_temperature": DHWTank.EXCESS_ENERGY_TARGET_TEMPERATURE,
        "excess_energy_target_temperature_hysteresis": DHWTank.EXCESS_ENERGY_TARGET_TEMPERATURE_HYSTERESIS,
        "excess_energy_mode": DHWTank.EXCESS_ENERGY_STATE,
        "heat_request": DHWTank.HEATING_REQUEST,
        "fresh_water_flow": DHWTank.FRESH_WATER_FLOW_ACTIVE,
        "fresh_water_module_temperature": DHWTank.FRESH_WATER_TEMPERATURE,
        "target_temperature": DHWTank.TARGET_TEMPERATURE,
        "standby_temperature": DHWTank.BACKUP_TEMPERATURE,
        "operating_mode": DHWTank.OPERATING_MODE,
        "current_temperature": DHWTank.TOP_TEMPERATURE,
        "circulation_return_temperature": DHWTank.CIRCULATION_RETURN_TEMPERATURE,
        "circulation_pump_state": DHWTank.CIRCULATION_PUMP_ACTIVE,
    },
    SectionPrefix.SWITCH_VALVE: {
        "position": SwitchValve.POSITION,
    },
    SectionPrefix.PHOTOVOLTAICS: {
        "excess_energy_active": Photovoltaics.EXCESS_ENERGY_ACTIVE,
        "excess_power": Photovoltaics.METER_EXCESS_POWER,
        "daily_energy": Photovoltaics.METER_DAILY_EXCESS_ENERGY,
        "total_energy": Photovoltaics.METER_ACCUMULATED_EXCESS_ENERGY,
    },
    SectionPrefix.SYSTEM: {
        "outdoor_temperature": System.OUTDOOR_TEMPERATURE,
        "operating_mode": System.OPERATING_MODE,
        "cpu_usage": System.CPU_USAGE,
        "webview_cpu_usage": System.WEBVIEW_CPU_USAGE,
        "webserver_cpu_usage": System.WEBSERVER_CPU_USAGE,
        "control_cpu_usage": System.CONTROL_CPU_USAGE,
        "ram_usage": System.TEMPORARY_MEMORY_USAGE,
        "free_ram": System.FREE_RAM,
        "flash_erase_counter": System.FLASH_MAX_ERASE_COUNTER,
    },
}


class KeyedDescription(Protocol):
    """Keys of an entity description."""

    @property
    def key(self) -> str:
        """Return the key of the value, part of the unique ID."""

    @property
    def new_key(self) -> str | None:
        """Return the new name of the value if the API renamed it."""


def get_state(member: Enum, /) -> str:
    """Return the state of an enum member, as the entities show it."""
    return LEGACY_STATES.get(member, member.name.lower())


def get_states(enum: type[Enum], /) -> list[str]:
    """Return the states of all members of an enum, as the entities show them."""
    return [get_state(member) for member in enum]


def get_member[E: Enum](enum: type[E], state: str, /) -> E:
    """Return the enum member of a state, as the entities show it."""
    return next(member for member in enum if get_state(member) == state)


def get_data_keys(description: KeyedDescription, /) -> tuple[str, ...]:
    """Return the keys of the coordinator data that an entity can use, the key and the new key if the API renamed it."""
    return tuple(key for key in (description.key, description.new_key) if key)


def get_data_key(description: KeyedDescription, /) -> str:
    """Return the key of the value in the coordinator data, the new key if the API renamed it."""
    return description.new_key or description.key
