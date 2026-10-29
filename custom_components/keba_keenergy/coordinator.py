# Copyright 2025-2026 Michael Hacker
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
from typing import Final
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
from keba_keenergy_api.constants import ExternalHeatSource
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatCircuitMode
from keba_keenergy_api.constants import HeatPump
from keba_keenergy_api.constants import HeatPumpState
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import MessageIdKind
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import System
from keba_keenergy_api.endpoints import HeatingCurves
from keba_keenergy_api.endpoints import Position
from keba_keenergy_api.endpoints import Value
from keba_keenergy_api.endpoints import ValueResponse
from keba_keenergy_api.error import APIError
from keba_keenergy_api.error import AuthenticationError

from .const import DEFAULT_SCAN_INTERVAL
from .const import DOMAIN
from .const import FLASH_WRITE_ISSUE_ID
from .const import FLASH_WRITE_LIMIT_PER_WEEK
from .const import REQUEST_DATA_GROUPS
from .const import REQUEST_REFRESH_COOLDOWN
from .const import SECTION_PREFIXES

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable

    from aiohttp import ClientSession
    from homeassistant.core import HomeAssistant

_LOGGER: Final = logging.getLogger(__name__)

type KebaKeEnergyConfigEntry = ConfigEntry[KebaKeEnergyDataUpdateCoordinator]
type MessageIds = list[int] | list[list[int]]
type Values = Value | list[Value] | list[list[Value]]


def get_device_identifier(entry_unique_id: str | None, section_id: str, position: int | None) -> str:
    """Return the device identifier `<entry unique_id>_<section or domain for the control unit>[_<position>]`.

    The position is only added if the section has more than one device.
    """
    identifier: str = f"{entry_unique_id}_{DOMAIN if section_id == SectionPrefix.SYSTEM else section_id}"
    return identifier if position is None else f"{identifier}_{position}"


def get_write_counter_store(hass: HomeAssistant, *, entry_id: str | None = None) -> Store[dict[str, Any]]:
    """Return the store of the write counter of a config entry, without entry ID the store shared by all entries.

    The shared store was used by older versions and is only removed.
    """
    return Store(hass, version=1, key=DOMAIN if entry_id is None else f"{DOMAIN}.{entry_id}")


def get_value_by_index(
    values: Values,
    /,
    *,
    index: int | None,
    key_index: int | None,
) -> Value:
    """Return the value of the device with the index, and of the key with the key index if the device has several."""
    value: Value | list[Value] = values[index or 0] if isinstance(values, list) else values
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

        self._store: Store[dict[str, Any]] = get_write_counter_store(hass, entry_id=entry.entry_id)
        self._write_lock: Lock = Lock()
        self._local_change_count: int = 0

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
        self._weekly_writes: dict[str, int] = {}
        self._write_count_week: tuple[int, int] | None = None
        self._flash_issue_active: bool = False

        self._fixed_data: dict[str, ValueResponse] = {}
        self._message_ids: dict[str, dict[str, MessageIds]] = {}
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
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=REQUEST_REFRESH_COOLDOWN,
                immediate=True,
            ),
        )

    @property
    def fixed_data(self) -> dict[str, ValueResponse]:
        """Return the values that are read once on setup."""
        return self._fixed_data

    @property
    def message_ids(self) -> dict[str, dict[str, MessageIds]]:
        """Return the message ids of the sensors, 0 means the sensor is in use."""
        return self._message_ids

    @property
    def weekly_write_count(self) -> int:
        """Return the number of writes in the current week."""
        return self._weekly_write_count

    @property
    def weekly_writes(self) -> dict[str, int]:
        """Return how often each value was written in the current week, sorted by name."""
        return dict(sorted(self._weekly_writes.items()))

    @property
    def _issue_id(self) -> str:
        """Return the ID of the repair issue for frequent write operations of this control unit."""
        return f"{FLASH_WRITE_ISSUE_ID}_{self.config_entry.entry_id}"

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
        names: Values = self.data[SectionPrefix.HEAT_PUMP]["name"]
        return [name for name in names if isinstance(name, dict)] if isinstance(names, list) else []

    @property
    def heat_pump_states(self) -> set[HeatPumpState]:
        """Return the states of all heat pumps."""
        return {
            HeatPumpState[
                str(
                    get_value_by_index(self.data[SectionPrefix.HEAT_PUMP]["state"], index=index, key_index=None).get(
                        "value",
                    ),
                ).upper()
            ]
            for index in range(self.device_count(SectionPrefix.HEAT_PUMP))
        }

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        store_data: dict[str, Any] = await self._store.async_load() or {}
        counter: dict[str, Any] | None = store_data.get("flash_write_counter")

        if isinstance(counter, dict):
            self._write_count_week = tuple(counter["week"])
            self._weekly_write_count = counter["count"]
            self._weekly_writes = counter.get("writes", {})

        # Older versions stored one counter and created one repair issue for all config entries.
        await get_write_counter_store(self.hass).async_remove()
        ir.async_delete_issue(self.hass, domain=DOMAIN, issue_id=FLASH_WRITE_ISSUE_ID)

        await self._api_call_for_update(self._async_fixed_data())

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
                ExternalHeatSource.HAS_EMISSIONS,
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

        # Group request data by device but only add data that are available for the heat pump setup.
        self.request_data_groups = {
            prefix: [section for section in sections if section in self.request_data]
            for prefix, sections in REQUEST_DATA_GROUPS.items()
            if self.has_device(prefix)
        }

    async def _async_update_data(self) -> dict[str, ValueResponse]:
        """Read all values from API to update coordinator data."""
        first_run: bool = self._tick_counter == 0
        self._tick_counter = (self._tick_counter + 1) % 1_000_000

        if self._reset_weekly_counter_if_needed():
            await self._async_save_write_counter()

        request: list[Section] = []
        section_ids: dict[Section, str] = {}

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
            section_ids.update(dict.fromkeys(section_data, section.value))

            _LOGGER.debug(
                "Requesting section '%s' (multiplier=%d, position=%d)",
                section.value,
                multiplier,
                self.device_count(section),
            )

        local_change_count: int = self._local_change_count
        response: dict[str, ValueResponse] = await self._async_read_data(request)

        message_ids: dict[Section, list[int]] = await self._api_call_for_update(
            self.api.read_message_ids(
                request=request,
                position=self.position,
            ),
        )

        # A value set during the reads (e.g. before its write) would be replaced by its previous value until the next
        # update, so the values are read again after the write.
        if self._local_change_count != local_change_count:
            _LOGGER.debug("Reading the values again, a value was set during the update")
            response = await self._async_read_data(request)

        # Skipped sections keep their previous message ids.
        for message_section, ids in message_ids.items():
            quantity: int = message_section.value.quantity
            self._message_ids.setdefault(section_ids[message_section], {})[message_section.name.lower()] = (
                ids if quantity == 1 else [ids[index : index + quantity] for index in range(0, len(ids), quantity)]
            )

        _LOGGER.debug(
            "Sensors not in use: %s",
            {str(message_section): ids for message_section, ids in message_ids.items() if any(ids)},
        )

        if self.data:
            for section_id, previous_section_data in self.data.items():
                if not response[section_id]:
                    response[section_id] = previous_section_data

        return response

    async def _async_read_data(self, request: list[Section], /) -> dict[str, ValueResponse]:
        # The read waits for a running write, so it gets the written value.
        async with self._write_lock:
            return await self._api_call_for_update(
                self.api.read_data(
                    request=request,
                    position=self.position,
                ),
            )

    async def _async_save_write_counter(self) -> None:
        await self._store.async_save(
            {
                "flash_write_counter": {
                    "week": list(self._write_count_week) if self._write_count_week else [],
                    "count": self._weekly_write_count,
                    "writes": self._weekly_writes,
                },
            },
        )

    def async_update_value(
        self,
        value: object,
        /,
        *,
        section_id: str,
        section: Section,
        index: int,
        key_index: int | None,
    ) -> object:
        """Optimistically update a single value into coordinator data, return the replaced value."""
        if section.value.human_readable:
            value = section.value.human_readable(value).name.lower()

        return self.async_set_value(
            value,
            section_id=section_id,
            key=section.name.lower(),
            index=index,
            key_index=key_index,
        )

    def async_set_value(
        self,
        value: object,
        /,
        *,
        section_id: str,
        key: str,
        index: int,
        key_index: int | None,
    ) -> object:
        """Set a single value, as stored in the coordinator data, and return the replaced value."""
        # Only copy the changed section, the other sections are shared with the previous data.
        data: dict[str, ValueResponse] = {**self.data, section_id: deepcopy(self.data[section_id])}
        entity_data: Value = get_value_by_index(data[section_id][key], index=index, key_index=key_index)
        previous_value: object = entity_data.get("value")
        entity_data["value"] = value
        self._local_change_count += 1

        self.async_set_updated_data(data)

        return previous_value

    async def async_execute_write(
        self,
        *,
        write_fn: Callable[[], Awaitable[None]],
        names: tuple[str, ...],
        ignore_weekly_write_count: bool = False,
    ) -> None:
        """Set the weekly counter and write to the NAND.

        The names of the written values are counted separately, a write of several values counts once in total.
        """
        async with self._write_lock:
            counter_changed: bool = self._reset_weekly_counter_if_needed()

            if not ignore_weekly_write_count:
                self._weekly_write_count += 1

                for name in names:
                    self._weekly_writes[name] = self._weekly_writes.get(name, 0) + 1

                counter_changed = True

            if counter_changed:
                await self._async_save_write_counter()
                self.async_update_listeners()

            _LOGGER.debug(
                "API write request %s (writes this week: %s)",
                names,
                self._weekly_write_count,
            )

            if self._weekly_write_count > FLASH_WRITE_LIMIT_PER_WEEK and not self._flash_issue_active:
                self._flash_issue_active = True
                self._create_issue()

            await self._api_call_for_user(write_fn())

    def _reset_weekly_counter_if_needed(self) -> bool:
        """Reset the write counter in a new week, return True if it was reset."""
        today: date = now().date()
        current_week: tuple[int, int] = today.isocalendar().year, today.isocalendar().week

        if self._write_count_week == current_week:
            return False

        self._write_count_week = current_week
        self._weekly_write_count = 0
        self._weekly_writes = {}
        self._flash_issue_active = False

        ir.async_delete_issue(
            self.hass,
            domain=DOMAIN,
            issue_id=self._issue_id,
        )

        return True

    def _create_issue(self) -> None:
        ir.async_create_issue(
            self.hass,
            domain=DOMAIN,
            issue_id=self._issue_id,
            is_fixable=False,
            translation_key=FLASH_WRITE_ISSUE_ID,
            translation_placeholders={
                "limit": str(FLASH_WRITE_LIMIT_PER_WEEK),
                "name": self.config_entry.title,
            },
            severity=ir.IssueSeverity.WARNING,
        )

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

    async def async_write_data(self, request: dict[Section, Any], *, ignore_weekly_write_count: bool = False) -> None:
        """Write data to the NAND from the KEBA KeEnergy control unit."""
        await self.async_execute_write(
            write_fn=lambda: self.api.write_data(request=request),
            names=self._write_names(request),
            ignore_weekly_write_count=ignore_weekly_write_count,
        )

    @staticmethod
    def _write_names(request: dict[Section, Any], /) -> tuple[str, ...]:
        """Return the names of the written values, `<section>[_<position>].<value>[_<counter>]`.

        A list has one value per device (`None` skips a device), sections with a quantity > 1 have several values
        per device, which get a counter.
        """
        names: list[str] = []

        for section, value in request.items():
            prefix: str = SECTION_PREFIXES[type(section)]
            key: str = section.name.lower()

            if not isinstance(value, list | tuple):
                names.append(f"{prefix}.{key}")
                continue

            quantity: int = section.value.quantity

            for index, item in enumerate(value):
                if item is None:
                    continue

                position, key_index = divmod(index, quantity)
                counter: str = f"_{key_index + 1}" if quantity > 1 else ""
                names.append(f"{prefix}_{position + 1}.{key}{counter}")

        return tuple(names)

    async def get_timezone(self) -> ZoneInfo:
        """Get the timezone from the Web HMI."""
        timezone: str = await self._api_call_for_user(self.api.system.get_timezone())
        return ZoneInfo(timezone)

    async def get_heating_curve_points(self) -> HeatingCurves:
        """Get the points of all heating curves from the Web HMI."""
        return await self._api_call_for_user(self.api.heat_circuit.get_heating_curve_points())

    async def set_away_date_range(self, *, start_timestamp: float, end_timestamp: float) -> None:
        """Set the away date range of all heating circuits, if it changed."""
        away_start_date: list[int] = [int(start_timestamp)] * self.device_count(SectionPrefix.HEAT_CIRCUIT)
        away_end_date: list[int] = [int(end_timestamp)] * self.device_count(SectionPrefix.HEAT_CIRCUIT)

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
            for index in range(self.device_count(SectionPrefix.HEAT_CIRCUIT))
        ]

    def device_identifiers(self) -> set[str]:
        """Return the identifiers of all devices that the control unit is configured with.

        The devices come from the positions and options that are read on setup, not from the polled data,
        so a section that is missing in a response never removes a device.
        """
        identifiers: set[str] = set()

        for prefix in SectionPrefix:
            device_numbers: int = (
                int(self.has_device(prefix))
                if prefix in (SectionPrefix.SYSTEM, SectionPrefix.PHOTOVOLTAICS)
                else self.device_count(prefix)
            )
            identifiers.update(
                get_device_identifier(
                    self.config_entry.unique_id,
                    prefix,
                    index + 1 if device_numbers > 1 else None,
                )
                for index in range(device_numbers)
            )

        return identifiers

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

    def _is_fixed_value_on(self, prefix: SectionPrefix, key: str, /, *, index: int | None = None) -> bool:
        """Return True if a value that is read once on setup is switched on."""
        return self._get_fixed_value(prefix, key, index=index) == BoolEnum.ON.name.lower()

    def _get_fixed_value(self, prefix: SectionPrefix, key: str, /, *, index: int | None = None) -> object:
        """Return a value that is read once on setup, of the device with the index if the value is a list."""
        data: Values | None = self._fixed_data.get(prefix, {}).get(key)

        if isinstance(data, list):
            data = data[index or 0]

        return data.get("value") if isinstance(data, dict) else None

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

    def has_emissions(self, *, index: int | None = None) -> bool:
        """Check if the external heat source has emissions."""
        return self._is_fixed_value_on(SectionPrefix.EXTERNAL_HEAT_SOURCE, "has_emissions", index=index)

    def has_cooling_circuits(self) -> bool:
        """Check if one heating circuit support cooling."""
        # Some KEBA KeEnergy software versions did not have an active or passive cooling options.
        # Cooling support can only be detected with the heating circuit mode.
        return any(
            self.is_cooling_circuit(index=index) for index in range(self.device_count(SectionPrefix.HEAT_CIRCUIT))
        )

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

    def get_message_id(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> int | None:
        """Return the message id of a sensor (0 means the sensor is in use), or None if the sensor has none."""
        ids: MessageIds | None = self._message_ids.get(section_id, {}).get(key)

        if not ids:
            return None

        message_id: int | list[int] = ids[index or 0]
        return message_id[key_index or 0] if isinstance(message_id, list) else message_id

    def get_message_id_kind(
        self,
        section_id: str,
        key: str,
        /,
        *,
        index: int | None,
        key_index: int | None,
    ) -> MessageIdKind | None:
        """Return the kind of the message id of a sensor, or None if the sensor has none."""
        message_id: int | None = self.get_message_id(section_id, key, index=index, key_index=key_index)
        return None if message_id is None else MessageIdKind.from_message_id(message_id)

    def is_sensor_in_use(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> bool:
        """Check if the control unit reports the sensor as in use (message id 0) or has no message id for it."""
        return self.get_message_id_kind(section_id, key, index=index, key_index=key_index) in (MessageIdKind.OK, None)

    def is_sensor_deactivated(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> bool:
        """Check if the control unit reports the sensor as deactivated (message id 10), i.e. not configured."""
        return self.get_message_id_kind(section_id, key, index=index, key_index=key_index) is MessageIdKind.DEACTIVATED
