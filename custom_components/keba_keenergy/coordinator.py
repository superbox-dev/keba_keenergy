# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""DataUpdateCoordinator for the KEBA KeEnergy integration."""

from __future__ import annotations

import logging
from asyncio import Lock
from dataclasses import replace
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
from keba_keenergy_api.client import KebaKeEnergyAPI
from keba_keenergy_api.enums import ElectricalEnergyMeterType
from keba_keenergy_api.enums import HeatingCircuitType
from keba_keenergy_api.enums import HeatMeterType
from keba_keenergy_api.enums import HeatPumpState
from keba_keenergy_api.enums import MessageIdKind
from keba_keenergy_api.exceptions import APIError
from keba_keenergy_api.exceptions import AuthenticationError
from keba_keenergy_api.sections import System

from .const import DEFAULT_DECIMALS
from .const import DEFAULT_SCAN_INTERVAL
from .const import DEVICE_TYPES
from .const import DOMAIN
from .const import FLASH_WRITE_ISSUE_ID
from .const import FLASH_WRITE_LIMIT_PER_WEEK
from .const import HEATING_CURVE_KEY
from .const import LEGACY_STATES
from .const import MIXER_SECTIONS
from .const import OPTION_SECTIONS
from .const import RATIO_DECIMALS
from .const import RATIO_SECTIONS
from .const import REQUEST_REFRESH_COOLDOWN
from .const import SCAN_INTERVAL_PREFIXES
from .const import SECTIONS
from .const import MixerPosition
from .const import SectionPrefix

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable
    from collections.abc import Iterable
    from collections.abc import Mapping
    from collections.abc import Sequence
    from enum import Enum

    from aiohttp import ClientSession
    from homeassistant.core import HomeAssistant
    from keba_keenergy_api.models import CurveTable
    from keba_keenergy_api.models import DeviceCounts
    from keba_keenergy_api.models import DeviceInfo
    from keba_keenergy_api.models import HmiInfo
    from keba_keenergy_api.models import Reading
    from keba_keenergy_api.models import Readings
    from keba_keenergy_api.models import SystemInfo
    from keba_keenergy_api.models import Value
    from keba_keenergy_api.models import WriteValue
    from keba_keenergy_api.sections import Section

_LOGGER: Final = logging.getLogger(__name__)

type KebaKeEnergyConfigEntry = ConfigEntry[KebaKeEnergyDataUpdateCoordinator]
# The readings per device type and key, one reading per device (and consumer).
type CoordinatorData = dict[str, dict[str, list[Reading]]]


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


def get_state(member: Enum, /) -> str:
    """Return the state of an enum member, as the entities show it."""
    return LEGACY_STATES.get(member, member.name.lower())


def get_states(enum: type[Enum], /) -> list[str]:
    """Return the states of all members of an enum, as the entities show them."""
    return [get_state(member) for member in enum]


def get_member[E: Enum](enum: type[E], state: str, /) -> E:
    """Return the enum member of a state, as the entities show it."""
    return next(member for member in enum if get_state(member) == state)


class KebaKeEnergyDataUpdateCoordinator(DataUpdateCoordinator[CoordinatorData]):
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
            verify_ssl=False,
            session=session,
        )
        self._api_device_info: DeviceInfo | None = None
        self._api_system_info: SystemInfo | None = None
        self._api_hmi_info: HmiInfo | None = None

        self._weekly_write_count: int = 0
        self._weekly_writes: dict[str, int] = {}
        self._write_count_week: tuple[int, int] | None = None
        self._flash_issue_active: bool = False

        self._options: CoordinatorData = {}
        self._tick_counter: int = 0

        # The polled sections of the installed devices that the Web HMI supports, per device type and key.
        self.request_data_groups: dict[SectionPrefix, dict[str, Section]] = {}

        self.device_counts: DeviceCounts | None = None
        self.available_heating_curves: tuple[str, ...] = ()
        # The curve tables with their points, read with the curves in use.
        self.curve_tables: dict[str, CurveTable] = {}

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
    def options(self) -> CoordinatorData:
        """Return the options of the control unit that are read once on setup."""
        return self._options

    @property
    def message_ids(self) -> dict[str, dict[str, list[int | None]]]:
        """Return the message ids of the values per device type and key, None if a value has none."""
        return {
            section_id: {
                key: [None if reading.message_id is None else reading.message_id.value for reading in readings]
                for key, readings in section_data.items()
            }
            for section_id, section_data in (self.data or {}).items()
        }

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
        return str(self._api_device_info["name"]) if self._api_device_info else ""

    @cached_property
    def device_name(self) -> str:
        """Return device name."""
        return str(self._api_system_info["name"]) if self._api_system_info else ""

    @cached_property
    def device_hmi_sw_version(self) -> str:
        """Return HMI software version."""
        return str(self._api_hmi_info["name"]).replace("KeEnergy.WebHmi_", "") if self._api_hmi_info else ""

    @cached_property
    def device_serial_number(self) -> str:
        """Return serial number."""
        return str(self._api_device_info["serNo"]) if self._api_device_info else ""

    @property
    def heat_pump_names(self) -> list[str]:
        """Return heat pump names."""
        return [str(reading.value) for reading in self.data[SectionPrefix.HEAT_PUMP].get("name", [])]

    @property
    def heat_pump_states(self) -> set[HeatPumpState]:
        """Return the states of all heat pumps."""
        return {
            reading.value
            for reading in self.data[SectionPrefix.HEAT_PUMP].get("state", [])
            if isinstance(reading.value, HeatPumpState)
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
        self._api_device_info = await self.api.get_device_info()
        self._api_system_info = await self.api.get_system_info()
        self._api_hmi_info = await self.api.get_hmi_info()
        self.device_counts = await self.api.get_device_counts()
        self.curve_tables = await self.api.get_curve_tables()
        self.available_heating_curves = tuple(self.curve_tables)

        _LOGGER.debug("Device counts: %s", self.device_counts)

        # One check for the polled values and the options, each unknown value costs one more request.
        supported: set[Section] = set(
            await self.api.filter_supported(
                [
                    section
                    for sections in (*SECTIONS.values(), *OPTION_SECTIONS.values())
                    for section in sections.values()
                ],
                counts=self.device_counts,
            ),
        )

        option_sections: dict[Section, tuple[str, str]] = self._get_request(OPTION_SECTIONS, supported)
        readings: Readings = await self.api.read(option_sections, counts=self.device_counts, limits="none")
        self._options = self._group_readings(readings, option_sections)

        _LOGGER.debug("Options: %s", self._options)

        has_outdoor_temperature: bool = self.has_outdoor_temperature()

        # Group the polled values by device but only add the values that are available for the heat pump setup.
        self.request_data_groups = {
            SectionPrefix(prefix): {
                key: section
                for key, section in sections.items()
                if section in supported and (section is not System.OUTDOOR_TEMPERATURE or has_outdoor_temperature)
            }
            for prefix, sections in SECTIONS.items()
            if self.has_device(prefix)
        }

    @staticmethod
    def _get_request(
        sections: Mapping[SectionPrefix, Mapping[str, Section]],
        supported: set[Section],
        /,
    ) -> dict[Section, tuple[str, str]]:
        """Return the supported sections with their device type and key."""
        return {
            section: (prefix, key)
            for prefix, prefix_sections in sections.items()
            for key, section in prefix_sections.items()
            if section in supported
        }

    async def _async_update_data(self) -> CoordinatorData:
        """Read all values from API to update coordinator data."""
        first_run: bool = self._tick_counter == 0
        self._tick_counter = (self._tick_counter + 1) % 1_000_000

        if self._reset_weekly_counter_if_needed():
            await self._async_save_write_counter()

        request: dict[Section, tuple[str, str]] = {}

        for prefix, sections in self.request_data_groups.items():
            tick_prefix: SectionPrefix = SCAN_INTERVAL_PREFIXES.get(prefix, prefix)
            multiplier: int = self.config_entry.options.get(f"scan_interval_tick_{tick_prefix}", 1)

            if not first_run and self._tick_counter % multiplier != 0:
                _LOGGER.debug(
                    "Skipping section '%s' this tick (multiplier=%d)",
                    prefix.value,
                    multiplier,
                )
                continue

            request.update({section: (prefix, key) for key, section in sections.items()})

            _LOGGER.debug(
                "Requesting section '%s' (multiplier=%d, position=%d)",
                prefix.value,
                multiplier,
                self.device_count(prefix),
            )

        local_change_count: int = self._local_change_count
        readings: Readings = await self._async_read(request)

        # A value set during the read (e.g. before its write) would be replaced by its previous value until the next
        # update, so the values are read again after the write.
        if self._local_change_count != local_change_count:
            _LOGGER.debug("Reading the values again, a value was set during the update")
            readings = await self._async_read(request)

        # The sensor of the heating curve in use shows its points.
        if any(key == HEATING_CURVE_KEY for _, key in request.values()):
            self.curve_tables = await self._api_call_for_update(self.api.get_curve_tables())

        _LOGGER.debug(
            "Sensors not in use: %s",
            {
                str(section): [None if reading.message_id is None else reading.message_id.value for reading in values]
                for section, values in readings.items()
                if any(reading.message_id and reading.message_id.kind is not MessageIdKind.OK for reading in values)
            },
        )

        # Skipped sections keep their previous values.
        data: CoordinatorData = {
            section_id: dict(section_data) for section_id, section_data in (self.data or {}).items()
        }

        for section_id, section_data in self._group_readings(readings, request).items():
            data.setdefault(section_id, {}).update(section_data)

        return data

    async def _async_read(self, request: Iterable[Section], /) -> Readings:
        # The read waits for a running write, so it gets the written value.
        async with self._write_lock:
            return await self._api_call_for_update(
                self.api.read(request, counts=self.device_counts, limits="writable", message_ids=True),
            )

    @classmethod
    def _group_readings(cls, readings: Readings, request: Mapping[Section, tuple[str, str]], /) -> CoordinatorData:
        """Return the readings per device type and key, with the values as the entities show them."""
        data: CoordinatorData = {}

        for section, section_readings in readings.items():
            section_id, key = request[section]
            data.setdefault(section_id, {})[key] = [cls._normalize(section, reading) for reading in section_readings]

        return data

    @staticmethod
    def _normalize(section: Section, reading: Reading, /) -> Reading:
        """Return the reading with the value as `keba_keenergy_api` 2.x returned it, e.g. rounded."""
        if not isinstance(reading.value, float):
            return reading

        if section in MIXER_SECTIONS:
            # The setpoint stays the raw value, it is shown as `position_percent`.
            return replace(
                reading,
                value=MixerPosition((reading.value >= 1) - (reading.value <= -1)),
                raw_value=reading.value,
            )

        return replace(
            reading,
            value=round(reading.value, RATIO_DECIMALS if section in RATIO_SECTIONS else DEFAULT_DECIMALS),
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

    def get_section(self, section_id: str, key: str, /) -> Section:
        """Return the section of a key."""
        return SECTIONS[SectionPrefix(section_id)][key]

    def get_reading(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> Reading | None:
        """Return the reading of the device with the index (and the consumer with the key index), None if missing."""
        readings: list[Reading] | None = self.data.get(section_id, {}).get(key)

        if not readings:
            return None

        quantity: int = self.get_section(section_id, key).value.quantity
        return readings[(index or 0) * quantity + (key_index or 0)]

    def async_set_value(
        self,
        value: Value,
        /,
        *,
        section_id: str,
        key: str,
        index: int | None,
        key_index: int | None,
    ) -> Value:
        """Set a single value in the coordinator data and return the replaced value."""
        readings: list[Reading] = self.data[section_id][key]
        position: int = (index or 0) * self.get_section(section_id, key).value.quantity + (key_index or 0)
        previous_value: Value = readings[position].value

        # Only copy the changed values, the other values are shared with the previous data.
        data: CoordinatorData = {
            **self.data,
            section_id: {
                **self.data[section_id],
                key: [
                    replace(reading, value=value) if i == position else reading for i, reading in enumerate(readings)
                ],
            },
        }
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

    async def async_write_data(
        self,
        section_id: str,
        values: Mapping[str, Sequence[WriteValue | None]],
        /,
        *,
        ignore_weekly_write_count: bool = False,
    ) -> None:
        """Write values of one device type to the NAND, one sequence per key with one value per device."""
        request: dict[Section, Sequence[WriteValue | None]] = {
            self.get_section(section_id, key): key_values for key, key_values in values.items()
        }
        await self.async_execute_write(
            write_fn=lambda: self.api.write(request),
            names=self._write_names(section_id, request, values),
            ignore_weekly_write_count=ignore_weekly_write_count,
        )

    @staticmethod
    def _write_names(
        section_id: str,
        request: Mapping[Section, Sequence[WriteValue | None]],
        values: Mapping[str, Sequence[WriteValue | None]],
        /,
    ) -> tuple[str, ...]:
        """Return the names of the written values, `<section>[_<position>].<key>[_<counter>]`.

        A system-wide value has no position, sections with a quantity > 1 have several values per device, which get
        a counter. `None` skips a device.
        """
        names: list[str] = []

        for (section, section_values), key in zip(request.items(), values, strict=True):
            if not section.value.has_device_index:
                names.append(f"{section_id}.{key}")
                continue

            quantity: int = section.value.quantity

            for index, item in enumerate(section_values):
                if item is None:
                    continue

                position, key_index = divmod(index, quantity)
                counter: str = f"_{key_index + 1}" if quantity > 1 else ""
                names.append(f"{section_id}_{position + 1}.{key}{counter}")

        return tuple(names)

    async def get_timezone(self) -> ZoneInfo:
        """Get the timezone from the Web HMI."""
        timezone: str = await self._api_call_for_user(self.api.get_timezone())
        return ZoneInfo(timezone)

    async def get_curve_tables(self) -> dict[str, CurveTable]:
        """Get the heating and cooling curves from the Web HMI, by name."""
        return await self._api_call_for_user(self.api.get_curve_tables())

    async def set_away_date_range(self, *, start_timestamp: float, end_timestamp: float) -> None:
        """Set the away date range of all heating circuits, if it changed."""
        away_start_date: list[int] = [int(start_timestamp)] * self.device_count(SectionPrefix.HEAT_CIRCUIT)
        away_end_date: list[int] = [int(end_timestamp)] * self.device_count(SectionPrefix.HEAT_CIRCUIT)

        if self._heat_circuit_values("away_start_date") != away_start_date or (
            self._heat_circuit_values("away_end_date") != away_end_date
        ):
            await self.async_write_data(
                SectionPrefix.HEAT_CIRCUIT,
                {
                    "away_start_date": away_start_date,
                    "away_end_date": away_end_date,
                },
            )

    def _heat_circuit_values(self, key: str, /) -> list[Value]:
        """Return the values of all heating circuits."""
        return [reading.value for reading in self.data[SectionPrefix.HEAT_CIRCUIT].get(key, [])]

    def device_identifiers(self) -> set[str]:
        """Return the identifiers of all devices that the control unit is configured with.

        The devices come from the device counts and options that are read on setup, not from the polled data,
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
        """Return the number of devices of the section, 0 for the device types without a position."""
        device_type: str | None = DEVICE_TYPES.get(SectionPrefix(prefix))
        return 0 if self.device_counts is None or device_type is None else getattr(self.device_counts, device_type)

    def has_device(self, prefix: SectionPrefix) -> bool:
        """Return True if the device group is available in this setup."""
        if prefix == SectionPrefix.SYSTEM:
            return True

        if prefix == SectionPrefix.PHOTOVOLTAICS:
            return self.has_photovoltaics()

        return self.device_count(prefix) > 0

    def _get_option(self, prefix: SectionPrefix, key: str, /, *, index: int | None = None) -> Value | None:
        """Return an option that is read once on setup, of the device with the index."""
        readings: list[Reading] = self._options.get(prefix, {}).get(key, [])
        return readings[index or 0].value if len(readings) > (index or 0) else None

    def has_outdoor_temperature(self) -> bool:
        """Check if outdoor temperature sensor is available."""
        return self._get_option(SectionPrefix.SYSTEM, "has_outdoor_temperature") is True

    def has_room_temperature(self, *, index: int | None = None) -> bool:
        """Check if room temperature sensor is available."""
        return self._get_option(SectionPrefix.HEAT_CIRCUIT, "has_room_temperature", index=index) is True

    def has_room_humidity(self, *, index: int | None = None) -> bool:
        """Check if room humidity sensor is available."""
        return self._get_option(SectionPrefix.HEAT_CIRCUIT, "has_room_humidity", index=index) is True

    def has_photovoltaics(self) -> bool:
        """Check if photovoltaics is available."""
        return self._get_option(SectionPrefix.SYSTEM, "has_photovoltaics") is True

    def has_mixer(self, *, index: int | None = None) -> bool:
        """Check if heating circuit mixer is available."""
        return self._get_option(SectionPrefix.HEAT_CIRCUIT, "has_mixer", index=index) is True

    def has_return_flow_temperature(self, *, index: int | None = None) -> bool:
        """Check if heating circuit return flow temperature sensor is available."""
        return self._get_option(SectionPrefix.HEAT_CIRCUIT, "has_return_flow_temperature", index=index) is True

    def has_pump(self, *, index: int | None = None) -> bool:
        """Check if heating circuit pump is available."""
        return self._get_option(SectionPrefix.HEAT_CIRCUIT, "has_pump", index=index) is True

    def has_var_speed_pump(self, *, index: int | None = None) -> bool:
        """Check if heating circuit variable speed pump is available."""
        return self._get_option(SectionPrefix.HEAT_CIRCUIT, "has_var_speed_pump", index=index) is True

    def has_fresh_water_module(self, *, index: int | None = None) -> bool:
        """Check if fresh water module is available."""
        return self._get_option(SectionPrefix.HOT_WATER_TANK, "has_fresh_water_module", index=index) is True

    def has_electrical_energy_meter(self, *, index: int | None = None) -> bool:
        """Check if electrical energy meter is available."""
        value: Value | None = self._get_option(SectionPrefix.HEAT_PUMP, "electric_energy_meter_type", index=index)
        return isinstance(value, ElectricalEnergyMeterType) and value is not ElectricalEnergyMeterType.NONE

    def has_heat_meter(self, *, index: int | None = None) -> bool:
        """Check if heat meter is available."""
        value: Value | None = self._get_option(SectionPrefix.HEAT_PUMP, "heat_meter_type", index=index)
        return isinstance(value, HeatMeterType) and value is not HeatMeterType.NONE

    def has_active_cooling(self, *, index: int | None = None) -> bool:
        """Check if active cooling is available."""
        return self._get_option(SectionPrefix.HEAT_PUMP, "has_active_cooling", index=index) is True

    def has_passive_cooling(self, *, index: int | None = None) -> bool:
        """Check if passive cooling is available."""
        return self._get_option(SectionPrefix.HEAT_PUMP, "has_passive_cooling", index=index) is True

    def has_emissions(self, *, index: int | None = None) -> bool:
        """Check if the external heat source has emissions."""
        return self._get_option(SectionPrefix.EXTERNAL_HEAT_SOURCE, "has_emissions", index=index) is True

    def has_cooling_circuits(self) -> bool:
        """Check if one heating circuit support cooling."""
        # Some KEBA KeEnergy software versions did not have an active or passive cooling options.
        # Cooling support can only be detected with the heating circuit mode.
        return any(
            self.is_cooling_circuit(index=index) for index in range(self.device_count(SectionPrefix.HEAT_CIRCUIT))
        )

    def is_cooling_circuit(self, *, index: int | None = None) -> bool:
        """Check if heating circuit mode is cooling."""
        return self._get_option(SectionPrefix.HEAT_CIRCUIT, "mode", index=index) in (
            HeatingCircuitType.COOLING,
            HeatingCircuitType.HEATING_AND_COOLING,
            HeatingCircuitType.HEATING_AND_ACTIVE_COOLING,
        )

    def is_heating_circuit(self, *, index: int | None = None) -> bool:
        """Check if heating circuit mode is heating."""
        return self._get_option(SectionPrefix.HEAT_CIRCUIT, "mode", index=index) in (
            HeatingCircuitType.HEATING,
            HeatingCircuitType.HEATING_AND_COOLING,
            HeatingCircuitType.HEATING_AND_ACTIVE_COOLING,
        )

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
        reading: Reading | None = self.get_reading(section_id, key, index=index, key_index=key_index)
        return None if reading is None or reading.message_id is None else reading.message_id.kind

    def is_sensor_in_use(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> bool:
        """Check if the control unit reports the sensor as in use (message id 0) or has no message id for it."""
        return self.get_message_id_kind(section_id, key, index=index, key_index=key_index) in (MessageIdKind.OK, None)

    def is_sensor_deactivated(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> bool:
        """Check if the control unit reports the sensor as deactivated (message id 10), i.e. not configured."""
        return self.get_message_id_kind(section_id, key, index=index, key_index=key_index) is MessageIdKind.DEACTIVATED
