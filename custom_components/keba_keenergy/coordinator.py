# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""DataUpdateCoordinator for the KEBA KeEnergy integration."""

from __future__ import annotations

import logging
from asyncio import Lock
from copy import deepcopy
from datetime import date
from datetime import timedelta
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any
from zoneinfo import ZoneInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.const import CONF_SSL
from homeassistant.const import CONF_USERNAME
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util.dt import now
from keba_keenergy_api.api import KebaKeEnergyAPI
from keba_keenergy_api.constants import BoolEnum
from keba_keenergy_api.constants import BufferTank
from keba_keenergy_api.constants import ExternalHeatSource
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatCircuitMode
from keba_keenergy_api.constants import HeatPump
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import PassiveCooling
from keba_keenergy_api.constants import Photovoltaics
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import SolarCircuit
from keba_keenergy_api.constants import SwitchValve
from keba_keenergy_api.constants import System
from keba_keenergy_api.endpoints import HeatingCurves
from keba_keenergy_api.endpoints import Position
from keba_keenergy_api.endpoints import Value
from keba_keenergy_api.endpoints import ValueResponse
from keba_keenergy_api.error import APIError
from keba_keenergy_api.error import AuthenticationError

from .const import DEFAULT_SCAN_INTERVAL
from .const import DOMAIN
from .const import FLASH_WRITE_LIMIT_PER_WEEK
from .const import REQUEST_REFRESH_COOLDOWN

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable

    from aiohttp import ClientSession
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

type KebaKeEnergyConfigEntry = ConfigEntry[KebaKeEnergyDataUpdateCoordinator]


REQUEST_DATA_GROUPS: dict[SectionPrefix, list[Section]] = {
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
        # Passive cooling has not an own group for the ticks
        # It is always a part of heat pumps
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
    ],
}


def get_value_by_index(
    values: list[list[Value]] | list[Value] | Value,
    /,
    *,
    index: int | None,
    key_index: int | None,
) -> Value:
    """Return the value of the device with the index, and of the key with the key index if the device has several."""
    value: list[Value] | Value = values[index or 0] if isinstance(values, list) else values
    return value[key_index or 0] if isinstance(value, list) else value


class KebaKeEnergyDataUpdateCoordinator(DataUpdateCoordinator[dict[str, ValueResponse]]):
    """Class to manage fetching KEBA KeEnergy data API."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: KebaKeEnergyConfigEntry,
        /,
        *,
        session: ClientSession,
    ) -> None:
        """Initialize the coordinator.

        Parameters
        ----------
        hass
            The Home Assistant instance.
        entry
            The config entry with the host, the SSL setting and the optional credentials.
        session
            The HTTP session for the requests to the Web HMI.

        """
        self.config_entry: KebaKeEnergyConfigEntry = entry
        self.control_unit_device_id: str = ""

        self._store: Store[dict[str, Any]] = Store(hass, version=1, key=DOMAIN)
        self._write_lock: Lock = Lock()

        self.api: KebaKeEnergyAPI = KebaKeEnergyAPI(
            entry.data[CONF_HOST],
            username=entry.data.get(CONF_USERNAME),
            password=entry.data.get(CONF_PASSWORD),
            ssl=entry.data[CONF_SSL],
            skip_ssl_verification=True,
            session=session,
        )
        self._api_device_info: dict[str, Any] = {}
        self._api_system_info: dict[str, Any] = {}
        self._api_hmi_info: dict[str, Any] = {}

        self._weekly_write_count: int = 0
        self._write_count_week: tuple[int, int] | None = None
        self._flash_issue_active: bool = False

        self._fixed_data: dict[str, ValueResponse] = {}
        self._tick_counter: int = 0

        self.request_data: list[Section] = [
            section for sections in REQUEST_DATA_GROUPS.values() for section in sections
        ]
        self.request_data_groups: dict[SectionPrefix, list[Section]] = {}

        self.position: Position | None = None
        self.available_heating_curves: tuple[tuple[int, str], ...] = ()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=REQUEST_REFRESH_COOLDOWN,
                immediate=True,
            ),
        )

    @staticmethod
    async def _api_call_for_update[R](coro: Awaitable[R]) -> R:
        try:
            return await coro
        except AuthenticationError as error:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="authentication_error",
            ) from error
        except APIError as error:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="communication_error",
                translation_placeholders={
                    "error": str(error),
                },
            ) from error

    @staticmethod
    async def _api_call_for_user[R](coro: Awaitable[R]) -> R:
        try:
            return await coro
        except APIError as error:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="communication_error",
                translation_placeholders={
                    "error": str(error),
                },
            ) from error

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        store_data: dict[str, Any] = await self._store.async_load() or {}
        counter: dict[str, Any] | None = store_data.get("flash_write_counter")

        if isinstance(counter, dict):
            self._write_count_week = tuple(counter["week"])
            self._weekly_write_count = counter["count"]

        await self._api_call_for_update(self._async_fixed_data())

    async def _async_fixed_data(self) -> None:
        self._api_device_info = await self.api.system.get_device_info()
        self._api_system_info = await self.api.system.get_info()
        self._api_hmi_info = await self.api.system.get_hmi_info()
        self.position = await self.api.system.get_positions()
        self.available_heating_curves = await self.api.heat_circuit.get_available_heating_curves()

        _LOGGER.debug("Position: %s", self.position)

        self.request_data = await self.api.filter_request(
            request=self.request_data,
            position=self.position,
        )

        fixed_request_data: list[Section] = await self.api.filter_request(
            request=[
                System.HAS_OUTDOOR_TEMPERATURE,
                System.HAS_PHOTOVOLTAICS,
                HeatCircuit.MODE,
                HeatCircuit.HAS_ROOM_TEMPERATURE,
                HeatCircuit.HAS_ROOM_HUMIDITY,
                HeatCircuit.HAS_MIXER,
                HeatCircuit.HAS_RETURN_FLOW_TEMPERATURE,
                HeatCircuit.HAS_PUMP,
                HeatCircuit.HAS_VAR_SPEED_PUMP,
                HotWaterTank.HAS_FRESH_WATER_MODULE,
                HeatPump.HAS_ACTIVE_COOLING,
                HeatPump.HAS_PASSIVE_COOLING,
                HeatPump.ELECTRIC_ENERGY_METER_TYPE,
                HeatPump.HEAT_METER_TYPE,
            ],
            position=self.position,
        )

        self._fixed_data = await self.api.read_data(
            request=fixed_request_data,
            position=self.position,
        )

        _LOGGER.debug("Options: %s", self._fixed_data)

        has_outdoor_temperature: bool = self.has_outdoor_temperature()
        self.request_data = [
            section for section in self.request_data if section != System.OUTDOOR_TEMPERATURE or has_outdoor_temperature
        ]

        # Group request data by device but only add data that are available for the heat pump setup
        self.request_data_groups = {
            prefix: [section for section in sections if section in self.request_data]
            for prefix, sections in REQUEST_DATA_GROUPS.items()
            if self.has_device(prefix)
        }

    async def _async_update_data(self) -> dict[str, ValueResponse]:
        """Read all values from API to update coordinator data."""
        first_run: bool = self._tick_counter == 0
        self._tick_counter = (self._tick_counter + 1) % 1_000_000

        request: list[Section] = []

        for section, section_data in self.request_data_groups.items():
            multiplier: int = self.config_entry.options.get(f"scan_interval_tick_{section.value}", 1)

            if not first_run and self._tick_counter % multiplier != 0:
                _LOGGER.debug(
                    "Skipping section '%s' this tick (multiplier=%d)",
                    section.value,
                    multiplier,
                )
                continue

            request.extend(section_data)

            _LOGGER.debug(
                "Requesting section '%s' (multiplier=%d, position=%d)",
                section.value,
                multiplier,
                self.device_count(section),
            )

        response: dict[str, ValueResponse] = await self._api_call_for_update(
            self.api.read_data(
                request=request,
                position=self.position,
            ),
        )

        if self.data:
            for section_id, previous_section_data in self.data.items():
                if not response[section_id]:
                    response[section_id] = previous_section_data

        return response

    def async_update_value(
        self,
        value: object,
        /,
        *,
        section_id: str,
        section: Section,
        index: int,
        key_index: int | None,
    ) -> None:
        """Optimistically update a single value into coordinator data."""
        # Only copy the changed section, the other sections are shared with the previous data
        data: dict[str, ValueResponse] = {**self.data, section_id: deepcopy(self.data[section_id])}
        key: str = section.name.lower()

        if section.value.human_readable:
            value = section.value.human_readable(value).name.lower()

        get_value_by_index(data[section_id][key], index=index, key_index=key_index)["value"] = value

        self.async_set_updated_data(data)

    async def async_execute_write(
        self,
        *,
        write_fn: Callable[[], Awaitable[None]],
        ignore_weekly_write_count: bool = False,
    ) -> None:
        """Set the weekly counter and write to the NAND."""
        async with self._write_lock:
            counter_changed: bool = self._reset_weekly_counter_if_needed()

            if not ignore_weekly_write_count:
                self._weekly_write_count += 1
                counter_changed = True

            if counter_changed:
                await self._store.async_save(
                    {
                        "flash_write_counter": {
                            "week": list(self._write_count_week) if self._write_count_week else [],
                            "count": self._weekly_write_count,
                        },
                    },
                )

            _LOGGER.debug(
                "API write request (writes this week: %s)",
                self._weekly_write_count,
            )

            if self._weekly_write_count > FLASH_WRITE_LIMIT_PER_WEEK and not self._flash_issue_active:
                self._flash_issue_active = True
                self._create_issue()

            await self._api_call_for_user(write_fn())

    async def async_write_data(self, request: dict[Section, Any], *, ignore_weekly_write_count: bool = False) -> None:
        """Write data to the NAND from the KEBA KeEnergy control unit."""
        await self.async_execute_write(
            write_fn=lambda: self.api.write_data(request=request),
            ignore_weekly_write_count=ignore_weekly_write_count,
        )

    def _create_issue(self) -> None:
        ir.async_create_issue(
            self.hass,
            domain=DOMAIN,
            issue_id="frequent_flash_writes",
            is_fixable=False,
            translation_key="frequent_flash_writes",
            translation_placeholders={
                "limit": str(FLASH_WRITE_LIMIT_PER_WEEK),
            },
            severity=ir.IssueSeverity.WARNING,
        )

    def _reset_weekly_counter_if_needed(self) -> bool:
        """Reset the write counter in a new week, return True if it was reset."""
        today: date = now().date()
        current_week: tuple[int, int] = today.isocalendar().year, today.isocalendar().week

        if self._write_count_week == current_week:
            return False

        self._write_count_week = current_week
        self._weekly_write_count = 0
        self._flash_issue_active = False

        ir.async_delete_issue(
            self.hass,
            domain=DOMAIN,
            issue_id="frequent_flash_writes",
        )

        return True

    async def get_timezone(self) -> ZoneInfo:
        """Get the timezone from the Web HMI."""
        timezone: str = await self._api_call_for_user(self.api.system.get_timezone())
        return ZoneInfo(timezone)

    async def get_heating_curve_points(self) -> HeatingCurves:
        """Get the points of all heating curves from the Web HMI."""
        return await self._api_call_for_user(self.api.heat_circuit.get_heating_curve_points())

    async def set_away_date_range(self, *, start_timestamp: float, end_timestamp: float) -> None:
        """Set the away date range of all heating circuits, if it changed."""
        away_start_date: list[int] = [int(start_timestamp)] * self.heat_circuit_numbers
        away_end_date: list[int] = [int(end_timestamp)] * self.heat_circuit_numbers

        if self._heat_circuit_values("away_start_date") != away_start_date or (
            self._heat_circuit_values("away_end_date") != away_end_date
        ):
            await self.async_write_data(
                request={
                    HeatCircuit.AWAY_START_DATE: away_start_date,
                    HeatCircuit.AWAY_END_DATE: away_end_date,
                },
            )

    def _heat_circuit_values(self, key: str, /) -> list[object]:
        """Return the values of all heating circuits."""
        return [
            get_value_by_index(self.data[SectionPrefix.HEAT_CIRCUIT][key], index=index, key_index=None).get("value")
            for index in range(self.heat_circuit_numbers)
        ]

    @property
    def fixed_data(self) -> dict[str, ValueResponse]:
        """Return the values that are read once on setup."""
        return self._fixed_data

    @property
    def weekly_write_count(self) -> int:
        """Return the number of writes in the current week."""
        return self._weekly_write_count

    @cached_property
    def configuration_url(self) -> str:
        """Return web gui url."""
        return str(self.api.device_url)

    @cached_property
    def device_model(self) -> str:
        """Return device model name."""
        return str(self._api_device_info["name"])

    @cached_property
    def device_name(self) -> str:
        """Return device name."""
        return str(self._api_system_info["name"])

    @cached_property
    def device_hmi_sw_version(self) -> str:
        """Return HMI software version."""
        return str(self._api_hmi_info["name"].replace("KeEnergy.WebHmi_", ""))

    @cached_property
    def device_serial_number(self) -> str:
        """Return serial number."""
        return str(self._api_device_info["serNo"])

    @property
    def heat_pump_names(self) -> list[Value]:
        """Return heat pump names."""
        names: list[list[Value]] | list[Value] | Value = self.data[SectionPrefix.HEAT_PUMP]["name"]
        return [name for name in names if isinstance(name, dict)] if isinstance(names, list) else []

    @cached_property
    def heat_circuit_numbers(self) -> int:
        """Return number of heat circuits."""
        return self.position.heat_circuit if self.position else 0

    @cached_property
    def buffer_tank_numbers(self) -> int:
        """Return number of buffer tanks."""
        return self.position.buffer_tank if self.position else 0

    @cached_property
    def hot_water_tank_numbers(self) -> int:
        """Return number of hot water tanks."""
        return self.position.hot_water_tank if self.position else 0

    def device_count(self, prefix: str, /) -> int:
        """Return the number of devices of the section."""
        count: object = getattr(self.position, prefix, 0)
        return count if isinstance(count, int) else 0

    def has_device(self, prefix: SectionPrefix) -> bool:
        """Return True if the device group is available in this setup."""
        if prefix == SectionPrefix.SYSTEM:
            return True

        if prefix == SectionPrefix.PHOTOVOLTAICS:
            return self.has_photovoltaics()

        return self.device_count(prefix) > 0

    def has_outdoor_temperature(self) -> bool:
        """Check if outdoor temperature sensor is available."""
        return self._is_fixed_value_on(SectionPrefix.SYSTEM, "has_outdoor_temperature")

    def has_room_temperature(self, *, index: int | None = None) -> bool:
        """Check if room temperature sensor is available."""
        return self._is_fixed_value_on(SectionPrefix.HEAT_CIRCUIT, "has_room_temperature", index=index)

    def has_room_humidity(self, *, index: int | None = None) -> bool:
        """Check if room humidity sensor is available."""
        return self._is_fixed_value_on(SectionPrefix.HEAT_CIRCUIT, "has_room_humidity", index=index)

    def has_photovoltaics(self) -> bool:
        """Check if photovoltaics is available."""
        return self._is_fixed_value_on(SectionPrefix.SYSTEM, "has_photovoltaics")

    def has_mixer(self, *, index: int | None = None) -> bool:
        """Check if heating circuit mixer is available."""
        return self._is_fixed_value_on(SectionPrefix.HEAT_CIRCUIT, "has_mixer", index=index)

    def has_return_flow_temperature(self, *, index: int | None = None) -> bool:
        """Check if heating circuit return flow temperature sensor is available."""
        return self._is_fixed_value_on(SectionPrefix.HEAT_CIRCUIT, "has_return_flow_temperature", index=index)

    def has_pump(self, *, index: int | None = None) -> bool:
        """Check if heating circuit pump is available."""
        return self._is_fixed_value_on(SectionPrefix.HEAT_CIRCUIT, "has_pump", index=index)

    def has_var_speed_pump(self, *, index: int | None = None) -> bool:
        """Check if heating circuit variable speed pump is available."""
        return self._is_fixed_value_on(SectionPrefix.HEAT_CIRCUIT, "has_var_speed_pump", index=index)

    def has_fresh_water_module(self, *, index: int | None = None) -> bool:
        """Check if fresh water module is available."""
        return self._is_fixed_value_on(SectionPrefix.HOT_WATER_TANK, "has_fresh_water_module", index=index)

    def has_electrical_energy_meter(self, *, index: int | None = None) -> bool:
        """Check if electrical energy meter is available."""
        value: object = self._get_fixed_value(SectionPrefix.HEAT_PUMP, "electric_energy_meter_type", index=index)
        return isinstance(value, int) and value > 0

    def has_heat_meter(self, *, index: int | None = None) -> bool:
        """Check if heat meter is available."""
        value: object = self._get_fixed_value(SectionPrefix.HEAT_PUMP, "heat_meter_type", index=index)
        return isinstance(value, int) and value > 0

    def has_active_cooling(self, *, index: int | None = None) -> bool:
        """Check if active cooling is available."""
        return self._is_fixed_value_on(SectionPrefix.HEAT_PUMP, "has_active_cooling", index=index)

    def has_passive_cooling(self, *, index: int | None = None) -> bool:
        """Check if passive cooling is available."""
        return self._is_fixed_value_on(SectionPrefix.HEAT_PUMP, "has_passive_cooling", index=index)

    def has_cooling_circuits(self) -> bool:
        """Check if one heating circuit support cooling."""
        # Some KEBA KeEnergy software versions did not have an active or passive cooling options.
        # Cooling support can only be detected with the heating circuit mode!
        return any(self.is_cooling_circuit(index=index) for index in range(self.heat_circuit_numbers))

    def is_cooling_circuit(self, *, index: int | None = None) -> bool:
        """Check if heating circuit mode is cooling."""
        return self._get_fixed_value(SectionPrefix.HEAT_CIRCUIT, "mode", index=index) in (
            HeatCircuitMode.COOLING.name.lower(),
            HeatCircuitMode.HEATING_AND_COOLING.name.lower(),
            HeatCircuitMode.HEATING_AND_ACTIVE_COOLING.name.lower(),
        )

    def is_heating_circuit(self, *, index: int | None = None) -> bool:
        """Check if heating circuit mode is heating."""
        return self._get_fixed_value(SectionPrefix.HEAT_CIRCUIT, "mode", index=index) in (
            HeatCircuitMode.HEATING.name.lower(),
            HeatCircuitMode.HEATING_AND_COOLING.name.lower(),
            HeatCircuitMode.HEATING_AND_ACTIVE_COOLING.name.lower(),
        )

    def _get_fixed_value(self, prefix: SectionPrefix, key: str, /, *, index: int | None = None) -> object:
        """Return a value that is read once on setup, of the device with the index if the value is a list."""
        data: list[list[Value]] | list[Value] | Value | None = self._fixed_data.get(prefix, {}).get(key)

        if isinstance(data, list):
            data = data[index or 0]

        return data.get("value") if isinstance(data, dict) else None

    def _is_fixed_value_on(self, prefix: SectionPrefix, key: str, /, *, index: int | None = None) -> bool:
        """Return True if a value that is read once on setup is switched on."""
        return self._get_fixed_value(prefix, key, index=index) == BoolEnum.ON.name.lower()
