# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""DataUpdateCoordinator for the KEBA KeEnergy integration."""

from __future__ import annotations

import logging
from asyncio import Lock
from dataclasses import replace
from datetime import timedelta
from typing import TYPE_CHECKING
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
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from keba_keenergy_api.client import KebaKeEnergyAPI
from keba_keenergy_api.enums import ElectricalEnergyMeterType
from keba_keenergy_api.enums import HeatingCircuitType
from keba_keenergy_api.enums import HeatMeterType
from keba_keenergy_api.enums import HeatPumpState
from keba_keenergy_api.enums import MessageIdKind
from keba_keenergy_api.exceptions import APIError
from keba_keenergy_api.exceptions import AuthenticationError
from keba_keenergy_api.models import CurveTable

from .const import CURVE_KEYS
from .const import DEFAULT_SCAN_INTERVAL
from .const import DEVICE_TYPES
from .const import DOMAIN
from .const import OPTION_SECTIONS
from .const import REQUEST_REFRESH_COOLDOWN
from .const import SCAN_INTERVAL_PREFIXES
from .const import SectionPrefix
from .legacy import SECTIONS
from .write_counter import FlashWriteCounter

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable
    from collections.abc import Iterable
    from collections.abc import Mapping
    from collections.abc import Sequence

    from aiohttp import ClientSession
    from homeassistant.core import HomeAssistant
    from keba_keenergy_api.models import CurvePoint
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


class KebaKeEnergyDataUpdateCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Read the values of a KEBA KeEnergy control unit and write changed values to it."""

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

        self.write_counter: FlashWriteCounter = FlashWriteCounter(hass, entry, on_change=self.async_update_listeners)
        self._write_lock: Lock = Lock()
        self._local_change_count: int = 0

        self._api: KebaKeEnergyAPI = KebaKeEnergyAPI(
            entry.data[CONF_HOST],
            username=entry.data.get(CONF_USERNAME),
            password=entry.data.get(CONF_PASSWORD),
            ssl=entry.data[CONF_SSL],
            verify_ssl=False,
            session=session,
        )
        self.configuration_url: str = str(self._api.device_url)

        # The device information, read once on setup.
        self.device_model: str = ""
        self.device_name: str = ""
        self.device_hmi_sw_version: str = ""
        self.device_serial_number: str = ""

        # The options of the control unit, read once on setup.
        self.options: CoordinatorData = {}
        self._tick_counter: int = 0

        # The polled sections of the installed devices that the Web HMI supports, per device type and key.
        self._polled_sections: dict[SectionPrefix, dict[str, Section]] = {}

        self.device_counts: DeviceCounts | None = None
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
    def curve_names(self) -> tuple[str, ...]:
        """Return the names of the heating and cooling curves."""
        return tuple(self.curve_tables)

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
        await self.write_counter.async_setup()
        await self._api_call_for_update(self._async_read_setup_data())

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

    async def _async_read_setup_data(self) -> None:
        device_info: DeviceInfo = await self._api.get_device_info()
        system_info: SystemInfo = await self._api.get_system_info()
        hmi_info: HmiInfo = await self._api.get_hmi_info()
        self.device_model = device_info["name"]
        self.device_serial_number = str(device_info["serNo"])
        self.device_name = system_info["name"]
        self.device_hmi_sw_version = hmi_info["name"].replace("KeEnergy.WebHmi_", "")
        self.device_counts = await self._api.get_device_counts()
        self.curve_tables = await self._api.get_curve_tables()

        # One check for the polled values and the options, each unknown value costs one more request.
        supported: set[Section] = set(
            await self._api.filter_supported(
                [
                    section
                    for sections in (*SECTIONS.values(), *OPTION_SECTIONS.values())
                    for section in sections.values()
                ],
                counts=self.device_counts,
            ),
        )

        option_sections: dict[Section, tuple[str, str]] = self._get_request(OPTION_SECTIONS, supported)
        readings: Readings = await self._api.read(option_sections, counts=self.device_counts, limits="none")
        self.options = self._group_readings(readings, option_sections)

        # Group the polled values by device but only add the values that are available for the heat pump setup.
        self._polled_sections = {
            SectionPrefix(prefix): {key: section for key, section in sections.items() if section in supported}
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

    @staticmethod
    def _group_readings(readings: Readings, request: Mapping[Section, tuple[str, str]], /) -> CoordinatorData:
        """Return the readings per device type and key."""
        data: CoordinatorData = {}

        for section, section_readings in readings.items():
            section_id, key = request[section]
            data.setdefault(section_id, {})[key] = section_readings

        return data

    async def _async_update_data(self) -> CoordinatorData:
        """Read all values from API to update coordinator data."""
        first_run: bool = self._tick_counter == 0
        self._tick_counter = (self._tick_counter + 1) % 1_000_000

        request: dict[Section, tuple[str, str]] = {}

        for prefix, sections in self._polled_sections.items():
            tick_prefix: SectionPrefix = SCAN_INTERVAL_PREFIXES.get(prefix, prefix)
            multiplier: int = self.config_entry.options.get(f"scan_interval_tick_{tick_prefix}", 1)

            if first_run or self._tick_counter % multiplier == 0:
                request.update({section: (prefix, key) for key, section in sections.items()})

        _LOGGER.debug("Requesting the sections %s", ", ".join(sorted({prefix for prefix, _ in request.values()})))

        local_change_count: int = self._local_change_count
        readings: Readings = await self._async_read(request)

        # A value set during the read (e.g. before its write) would be replaced by its previous value until the next
        # update, so the values are read again after the write.
        if self._local_change_count != local_change_count:
            _LOGGER.debug("Reading the values again, a value was set during the update")
            readings = await self._async_read(request)

        # The sensors of the curves in use show their points.
        if any(key in CURVE_KEYS for _, key in request.values()):
            self.curve_tables = await self._api_call_for_update(self._api.get_curve_tables())

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
                self._api.read(request, counts=self.device_counts, limits="writable", message_ids=True),
            )

    @staticmethod
    def get_section(section_id: str, key: str, /) -> Section:
        """Return the section of a key."""
        return SECTIONS[SectionPrefix(section_id)][key]

    def get_reading(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> Reading | None:
        """Return the reading of the device with the index (and the consumer with the key index), None if missing."""
        readings: list[Reading] | None = self.data.get(section_id, {}).get(key)

        if not readings:
            return None

        return readings[self._reading_index(section_id, key, index=index, key_index=key_index)]

    def _reading_index(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> int:
        """Return the index in the readings of the key, of the device (and the consumer with the key index)."""
        return (index or 0) * self.get_section(section_id, key).value.quantity + (key_index or 0)

    def async_set_local_value(
        self,
        value: Value,
        /,
        *,
        section_id: str,
        key: str,
        index: int | None,
        key_index: int | None,
    ) -> Value:
        """Set a single value in the coordinator data, without writing it, and return the replaced value."""
        readings: list[Reading] = self.data[section_id][key]
        reading_index: int = self._reading_index(section_id, key, index=index, key_index=key_index)
        previous_value: Value = readings[reading_index].value

        # Only copy the changed values, the other values are shared with the previous data.
        data: CoordinatorData = {
            **self.data,
            section_id: {
                **self.data[section_id],
                key: [
                    replace(reading, value=value) if i == reading_index else reading
                    for i, reading in enumerate(readings)
                ],
            },
        }
        self._local_change_count += 1

        self.async_set_updated_data(data)

        return previous_value

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
        await self._async_execute_write(
            write_fn=lambda: self._api.write(request),
            names=self._write_names(section_id, request, values),
            ignore_weekly_write_count=ignore_weekly_write_count,
        )

    async def _async_execute_write(
        self,
        *,
        write_fn: Callable[[], Awaitable[None]],
        names: tuple[str, ...],
        ignore_weekly_write_count: bool = False,
    ) -> None:
        async with self._write_lock:
            if not ignore_weekly_write_count:
                await self.write_counter.async_add_write(names)

            _LOGGER.debug(
                "API write request %s (writes this week: %s)",
                names,
                self.write_counter.weekly_count,
            )

            await self._api_call_for_user(write_fn())

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

    @staticmethod
    def _write_names(
        section_id: str,
        request: Mapping[Section, Sequence[WriteValue | None]],
        values: Mapping[str, Sequence[WriteValue | None]],
        /,
    ) -> tuple[str, ...]:
        """Return the names of the written values, `<section>[_<device number>].<key>[_<counter>]`.

        A system-wide value has no device number, sections with a quantity > 1 have several values per device, which get
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

                device_index, key_index = divmod(index, quantity)
                counter: str = f"_{key_index + 1}" if quantity > 1 else ""
                names.append(f"{section_id}_{device_index + 1}.{key}{counter}")

        return tuple(names)

    async def async_set_curve_table_points(self, name: str, points: Sequence[CurvePoint], /) -> None:
        """Write the points of a heating or cooling curve to the NAND."""
        await self._async_execute_write(
            write_fn=lambda: self._api.set_curve_table_points(name, points),
            names=(f"heating_curve_points.{name}",),
        )

        # The sensors of the curve show the written points without reading them again.
        self.curve_tables = {**self.curve_tables, name: CurveTable(name=name, points=tuple(points))}
        self.async_update_listeners()

    async def async_set_away_date_range(self, *, start_timestamp: float, end_timestamp: float) -> None:
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

    async def async_get_timezone(self) -> ZoneInfo:
        """Get the timezone from the Web HMI."""
        timezone: str = await self._api_call_for_user(self._api.get_timezone())
        return ZoneInfo(timezone)

    async def async_read_curve_tables(self) -> dict[str, CurveTable]:
        """Read the heating and cooling curves from the Web HMI, by name."""
        return await self._api_call_for_user(self._api.get_curve_tables())

    def device_identifier(self, section_id: str, device_number: int | None, /) -> str:
        """Return the device identifier `<entry unique_id>_<section or domain for the control unit>[_<device number>]`.

        The device number is only added if the section has more than one device.
        """
        identifier: str = (
            f"{self.config_entry.unique_id}_{DOMAIN if section_id == SectionPrefix.SYSTEM else section_id}"
        )
        return identifier if device_number is None else f"{identifier}_{device_number}"

    def device_identifiers(self) -> set[str]:
        """Return the identifiers of all devices that the control unit is configured with.

        The devices come from the device counts and options that are read on setup, not from the polled data,
        so a section that is missing in a response never removes a device.
        """
        identifiers: set[str] = set()

        for prefix in SectionPrefix:
            count: int = (
                int(self.has_device(prefix))
                if prefix in (SectionPrefix.SYSTEM, SectionPrefix.PHOTOVOLTAICS)
                else self.device_count(prefix)
            )
            identifiers.update(
                self.device_identifier(prefix, index + 1 if count > 1 else None) for index in range(count)
            )

        return identifiers

    def device_count(self, prefix: str, /) -> int:
        """Return the number of devices of the section, 0 for the device types without a device number."""
        device_type: str | None = DEVICE_TYPES.get(SectionPrefix(prefix))
        return 0 if self.device_counts is None or device_type is None else getattr(self.device_counts, device_type)

    def has_device(self, prefix: str, /) -> bool:
        """Return True if the device group is available in this setup."""
        if prefix == SectionPrefix.SYSTEM:
            return True

        if prefix == SectionPrefix.PHOTOVOLTAICS:
            return self.has_photovoltaics()

        return self.device_count(prefix) > 0

    def has_photovoltaics(self) -> bool:
        """Check if photovoltaics is available."""
        return self._get_option(SectionPrefix.SYSTEM, "has_photovoltaics") is True

    def _get_option(self, prefix: SectionPrefix, key: str, /, *, index: int | None = None) -> Value | None:
        """Return an option that is read once on setup, of the device with the index."""
        readings: list[Reading] = self.options.get(prefix, {}).get(key, [])
        return readings[index or 0].value if len(readings) > (index or 0) else None

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
        """Check if one heating circuit supports cooling."""
        # Some KEBA KeEnergy software versions do not have the options for active and passive cooling.
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

    def is_sensor_in_use(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> bool:
        """Check if the control unit reports the sensor as in use (message id 0) or has no message id for it."""
        return self._get_message_id_kind(section_id, key, index=index, key_index=key_index) in (MessageIdKind.OK, None)

    def _get_message_id_kind(
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

    def is_sensor_deactivated(self, section_id: str, key: str, /, *, index: int | None, key_index: int | None) -> bool:
        """Check if the control unit reports the sensor as deactivated (message id 10), i.e. not configured."""
        return self._get_message_id_kind(section_id, key, index=index, key_index=key_index) is MessageIdKind.DEACTIVATED
