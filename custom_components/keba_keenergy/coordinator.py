# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""DataUpdateCoordinator for the KEBA KeEnergy integration."""

from __future__ import annotations

import logging
from asyncio import Lock
from dataclasses import replace
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Final
from zoneinfo import ZoneInfo
from zoneinfo import ZoneInfoNotFoundError

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
from homeassistant.util import dt as dt_util
from keba_keenergy_api.client import KebaKeEnergyAPI
from keba_keenergy_api.enums import ElectricalEnergyMeterType
from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import HeatingCircuitType
from keba_keenergy_api.enums import HeatMeterType
from keba_keenergy_api.enums import HeatPumpState
from keba_keenergy_api.enums import MessageIdKind
from keba_keenergy_api.enums import WeekDay
from keba_keenergy_api.enums import WeekTimerType
from keba_keenergy_api.exceptions import APIError
from keba_keenergy_api.exceptions import AuthenticationError
from keba_keenergy_api.models import CurveTable

from .const import CONFIGURATION_ENDPOINTS
from .const import CURVE_KEYS
from .const import DEFAULT_SCAN_INTERVAL
from .const import DEVICE_TYPES
from .const import DOMAIN
from .const import REQUEST_REFRESH_COOLDOWN
from .const import SCAN_INTERVAL_DEVICE_TYPES
from .const import SCAN_INTERVAL_TICK_OPTIONS
from .const import SectionPrefix
from .legacy import ENDPOINTS
from .write_counter import FlashWriteCounter

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable
    from collections.abc import Iterable
    from collections.abc import Mapping
    from collections.abc import Sequence

    from aiohttp import ClientSession
    from homeassistant.core import HomeAssistant
    from keba_keenergy_api.endpoints import Endpoint
    from keba_keenergy_api.models import CurvePoint
    from keba_keenergy_api.models import DeviceCounts
    from keba_keenergy_api.models import DeviceInfo
    from keba_keenergy_api.models import HmiInfo
    from keba_keenergy_api.models import Reading
    from keba_keenergy_api.models import Readings
    from keba_keenergy_api.models import SystemInfo
    from keba_keenergy_api.models import Value
    from keba_keenergy_api.models import WeekTimer
    from keba_keenergy_api.models import WriteValue

_LOGGER: Final = logging.getLogger(__name__)

type KebaKeEnergyConfigEntry = ConfigEntry[KebaKeEnergyDataUpdateCoordinator]
# The readings per device type and key, one reading per device (and consumer).
type CoordinatorData = dict[SectionPrefix, dict[str, list[Reading]]]
# The endpoints of a read with the device type and the key of their readings.
type ReadRequest = dict[Endpoint, tuple[SectionPrefix, str]]
# The values of a write per key, one value per device (and consumer), None skips it.
type WriteValues = Mapping[str, Sequence[WriteValue | None]]


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
        """Initialize the coordinator of the config entry, `session` is the HTTP session for the Web HMI."""
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

        # The configuration of the control unit, read once on setup.
        self.configuration: CoordinatorData = {}

        # The number of updates, for the scan interval multipliers of the device types.
        self._tick_counter: int = 0

        # The polled endpoints of the installed devices that the Web HMI supports, per device type and key.
        self._polled_endpoints: dict[SectionPrefix, dict[str, Endpoint]] = {}

        self.device_counts: DeviceCounts | None = None
        # The names of all heating and cooling curves and the points of the curves in use, read with every update of
        # the heating circuits.
        self.curve_names: tuple[str, ...] = ()
        self.curve_tables: dict[str, CurveTable] = {}

        # The time zone of the control unit, read once on setup (None if it is invalid), and the week timers of the
        # heating circuits by device number, read with every update of the heating circuits.
        self.timezone: ZoneInfo | None = None
        self.week_timers: dict[WeekTimerType, dict[int, WeekTimer]] = {}

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
    def heat_pump_names(self) -> list[str]:
        """Return the names of all heat pumps."""
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

        try:
            self.timezone = ZoneInfo(await self._api.get_timezone())
        except ValueError, ZoneInfoNotFoundError:
            _LOGGER.warning("The control unit has an invalid time zone, the week timers are not used")

        # One check for the polled values and the configuration, each unknown value costs one more request.
        supported: set[Endpoint] = set(
            await self._api.filter_supported(
                [
                    endpoint
                    for endpoints in (*ENDPOINTS.values(), *CONFIGURATION_ENDPOINTS.values())
                    for endpoint in endpoints.values()
                ],
                counts=self.device_counts,
            ),
        )

        configuration_request: ReadRequest = self._get_request(CONFIGURATION_ENDPOINTS, supported)
        readings: Readings = await self._api.read(configuration_request, counts=self.device_counts, limits="none")
        self.configuration = self._group_readings(readings, configuration_request)

        # Group the polled values by device but only add the values that are available for the heat pump setup.
        self._polled_endpoints = {
            device_type: {key: endpoint for key, endpoint in endpoints.items() if endpoint in supported}
            for device_type, endpoints in ENDPOINTS.items()
            if self.has_device(device_type)
        }

    @staticmethod
    def _get_request(
        endpoints: Mapping[SectionPrefix, Mapping[str, Endpoint]],
        supported: set[Endpoint],
        /,
    ) -> ReadRequest:
        """Return the supported endpoints with their device type and key."""
        return {
            endpoint: (device_type, key)
            for device_type, device_type_endpoints in endpoints.items()
            for key, endpoint in device_type_endpoints.items()
            if endpoint in supported
        }

    @staticmethod
    def _group_readings(readings: Readings, request: ReadRequest, /) -> CoordinatorData:
        """Return the readings per device type and key."""
        data: CoordinatorData = {}

        for endpoint, endpoint_readings in readings.items():
            device_type, key = request[endpoint]
            data.setdefault(device_type, {})[key] = endpoint_readings

        return data

    async def _async_update_data(self) -> CoordinatorData:
        """Read the values of the device types that are due in this update."""
        first_run: bool = self._tick_counter == 0
        self._tick_counter = (self._tick_counter + 1) % 1_000_000

        request: ReadRequest = {}

        for device_type, endpoints in self._polled_endpoints.items():
            tick_device_type: SectionPrefix = SCAN_INTERVAL_DEVICE_TYPES.get(device_type, device_type)
            multiplier: int = self.config_entry.options.get(SCAN_INTERVAL_TICK_OPTIONS[tick_device_type], 1)

            if first_run or self._tick_counter % multiplier == 0:
                request.update({endpoint: (device_type, key) for key, endpoint in endpoints.items()})

        _LOGGER.debug(
            "Requesting the device types %s", ", ".join(sorted({device_type for device_type, _ in request.values()}))
        )

        local_change_count: int = self._local_change_count
        readings: Readings = await self._async_read(request)

        # A value set during the read (e.g. before its write) would be replaced by its previous value until the next
        # update, so the values are read again after the write.
        if self._local_change_count != local_change_count:
            _LOGGER.debug("Reading the values again, a value was set during the update")
            readings = await self._async_read(request)

        # Skipped device types keep their previous values.
        data: CoordinatorData = {
            device_type: dict(readings_by_key) for device_type, readings_by_key in (self.data or {}).items()
        }

        for device_type, readings_by_key in self._group_readings(readings, request).items():
            data.setdefault(device_type, {}).update(readings_by_key)

        if any(key in CURVE_KEYS for _, key in request.values()):
            await self._async_read_curves(data)

        if any(device_type is SectionPrefix.HEATING_CIRCUIT for device_type, _ in request.values()):
            await self._async_read_week_timers()

        return data

    async def _async_read_week_timers(self) -> None:
        # The week timers tell if a heating circuit is currently in day or night operation.
        week_timers: dict[WeekTimerType, dict[int, WeekTimer]] = {}

        for timer_type, is_supported in (
            (WeekTimerType.HEATING_CIRCUIT_HEATING, self.is_heating_circuit),
            (WeekTimerType.HEATING_CIRCUIT_COOLING, self.is_cooling_circuit),
        ):
            device_numbers: list[int] = [
                index + 1
                for index in range(self.device_count(SectionPrefix.HEATING_CIRCUIT))
                if is_supported(index=index)
            ]

            if device_numbers:
                week_timers[timer_type] = await self._api_call_for_update(
                    self._api.get_week_timers(timer_type, device_numbers),
                )

        self.week_timers = week_timers

    def get_scheduled_operating_mode(
        self,
        *,
        index: int | None,
        cooling: bool,
    ) -> HeatingCircuitOperatingMode | None:
        """Return normal (day) or reduced (night) operation of the week timer of a heating circuit right now.

        None if there is no week timer or time zone, e.g. an invalid time zone or an older software version.
        """
        timer_type: WeekTimerType = (
            WeekTimerType.HEATING_CIRCUIT_COOLING if cooling else WeekTimerType.HEATING_CIRCUIT_HEATING
        )
        timer: WeekTimer | None = self.week_timers.get(timer_type, {}).get((index or 0) + 1)

        if timer is None or self.timezone is None:
            return None

        now: datetime = dt_util.now(self.timezone)
        # The week of the Web HMI starts with Sunday, Python with Monday.
        day: WeekDay = WeekDay((now.weekday() + 1) % 7)
        seconds_of_day: int = now.hour * 3600 + now.minute * 60 + now.second

        return (
            HeatingCircuitOperatingMode.NORMAL
            if any(block.start <= seconds_of_day < block.stop for block in timer.days[day].blocks)
            else HeatingCircuitOperatingMode.REDUCED
        )

    async def _async_read_curves(self, data: CoordinatorData, /) -> None:
        # The selects show the names of all curves, the sensors the points of the curves in use.
        self.curve_names = await self._api_call_for_update(self._api.get_curve_table_names())
        in_use: list[str] = [
            reading.value
            for readings_by_key in data.values()
            for key, readings in readings_by_key.items()
            if key in CURVE_KEYS
            for reading in readings
            if isinstance(reading.value, str) and reading.value in self.curve_names
        ]
        self.curve_tables = await self._api_call_for_update(self._api.get_curve_tables(in_use)) if in_use else {}

    async def _async_read(self, request: Iterable[Endpoint], /) -> Readings:
        # The read waits for a running write, so it gets the written value.
        async with self._write_lock:
            return await self._api_call_for_update(
                self._api.read(request, counts=self.device_counts, limits="writable", message_ids=True),
            )

    @staticmethod
    def get_endpoint(device_type: SectionPrefix, key: str, /) -> Endpoint:
        """Return the endpoint of a key."""
        return ENDPOINTS[device_type][key]

    def get_reading(
        self, device_type: SectionPrefix, key: str, /, *, index: int | None, value_index: int | None
    ) -> Reading | None:
        """Return the reading of the device with the index (and the value with the value index), None if missing."""
        readings: list[Reading] | None = self.data.get(device_type, {}).get(key)

        if not readings:
            return None

        return readings[self.reading_index(device_type, key, index=index, value_index=value_index)]

    def reading_index(
        self, device_type: SectionPrefix, key: str, /, *, index: int | None, value_index: int | None
    ) -> int:
        """Return the index in the readings of the key, of the device (and the value with the value index)."""
        return (index or 0) * self.get_endpoint(device_type, key).value.quantity + (value_index or 0)

    def async_set_local_value(
        self,
        value: Value,
        /,
        *,
        device_type: SectionPrefix,
        key: str,
        index: int | None,
        value_index: int | None,
    ) -> Value:
        """Set a single value in the coordinator data, without writing it, and return the replaced value."""
        readings: list[Reading] = self.data[device_type][key]
        reading_index: int = self.reading_index(device_type, key, index=index, value_index=value_index)
        previous_value: Value = readings[reading_index].value

        # Only copy the changed values, the other values are shared with the previous data.
        data: CoordinatorData = {
            **self.data,
            device_type: {
                **self.data[device_type],
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
        device_type: SectionPrefix,
        values: WriteValues,
        /,
        *,
        ignore_weekly_write_count: bool = False,
    ) -> None:
        """Write values of one device type to the NAND, one sequence per key with one value per device."""
        request: dict[Endpoint, Sequence[WriteValue | None]] = {
            self.get_endpoint(device_type, key): key_values for key, key_values in values.items()
        }
        await self._async_execute_write(
            write_fn=lambda: self._api.write(request),
            names=self._write_names(device_type, request, values),
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
            _LOGGER.debug("API write request %s", names)

            # A failed write raises here and is not counted, it does not change the flash memory.
            await self._api_call_for_user(write_fn())

            if not ignore_weekly_write_count:
                await self.write_counter.async_add_write(names)

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
        device_type: SectionPrefix,
        request: Mapping[Endpoint, Sequence[WriteValue | None]],
        values: WriteValues,
        /,
    ) -> tuple[str, ...]:
        """Return the names of the written values, `<device type>[_<device number>].<key>[_<counter>]`.

        A system-wide value has no device number, endpoints with a quantity > 1 have several values per device, which
        get a counter. `None` skips a device.
        """
        names: list[str] = []

        for (endpoint, endpoint_values), key in zip(request.items(), values, strict=True):
            if not endpoint.value.has_device_index:
                names.append(f"{device_type}.{key}")
                continue

            quantity: int = endpoint.value.quantity

            for index, item in enumerate(endpoint_values):
                if item is None:
                    continue

                device_index, value_index = divmod(index, quantity)
                counter: str = f"_{value_index + 1}" if quantity > 1 else ""
                names.append(f"{device_type}_{device_index + 1}.{key}{counter}")

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
        away_start_date: list[int] = [int(start_timestamp)] * self.device_count(SectionPrefix.HEATING_CIRCUIT)
        away_end_date: list[int] = [int(end_timestamp)] * self.device_count(SectionPrefix.HEATING_CIRCUIT)

        if self._heating_circuit_values("away_start_date") != away_start_date or (
            self._heating_circuit_values("away_end_date") != away_end_date
        ):
            await self.async_write_data(
                SectionPrefix.HEATING_CIRCUIT,
                {
                    "away_start_date": away_start_date,
                    "away_end_date": away_end_date,
                },
            )

            # The written date range is known before the next update, so the same date range is not written again.
            for key, timestamp in (("away_start_date", start_timestamp), ("away_end_date", end_timestamp)):
                for index in range(self.device_count(SectionPrefix.HEATING_CIRCUIT)):
                    self.async_set_local_value(
                        int(timestamp),
                        device_type=SectionPrefix.HEATING_CIRCUIT,
                        key=key,
                        index=index,
                        value_index=None,
                    )

    def _heating_circuit_values(self, key: str, /) -> list[Value]:
        """Return the values of all heating circuits."""
        return [reading.value for reading in self.data[SectionPrefix.HEATING_CIRCUIT].get(key, [])]

    async def async_get_timezone(self) -> ZoneInfo:
        """Read the time zone from the Web HMI."""
        timezone: str = await self._api_call_for_user(self._api.get_timezone())

        try:
            return ZoneInfo(timezone)
        except (ValueError, ZoneInfoNotFoundError) as error:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="invalid_time_zone",
                translation_placeholders={
                    "time_zone": timezone,
                },
            ) from error

    async def async_read_curve_table(self, name: str, /) -> CurveTable | None:
        """Read a heating or cooling curve from the Web HMI, None if there is no curve with the name."""
        if name not in await self._api_call_for_user(self._api.get_curve_table_names()):
            return None

        curve_tables: dict[str, CurveTable] = await self._api_call_for_user(self._api.get_curve_tables([name]))
        return curve_tables[name]

    def device_identifier(self, device_type: SectionPrefix, device_number: int | None, /) -> str:
        """Return the device identifier `<entry unique_id>_<device type>[_<device number>]`.

        The control unit has the domain as device type, the device number is only added if the device type has more
        than one device.
        """
        identifier: str = (
            f"{self.config_entry.unique_id}_{DOMAIN if device_type == SectionPrefix.SYSTEM else device_type}"
        )
        return identifier if device_number is None else f"{identifier}_{device_number}"

    def device_identifiers(self) -> set[str]:
        """Return the identifiers of all devices that the control unit is configured with.

        The devices come from the device counts and the configuration that are read on setup, not from the polled data,
        so a device type that is missing in a response never removes a device.
        """
        identifiers: set[str] = set()

        for device_type in SectionPrefix:
            count: int = (
                int(self.has_device(device_type))
                if device_type in (SectionPrefix.SYSTEM, SectionPrefix.PHOTOVOLTAICS)
                else self.device_count(device_type)
            )
            identifiers.update(
                self.device_identifier(device_type, index + 1 if count > 1 else None) for index in range(count)
            )

        return identifiers

    def device_count(self, device_type: SectionPrefix, /) -> int:
        """Return the number of devices of the device type, 0 for the device types without a device number."""
        api_device_type: str | None = DEVICE_TYPES.get(device_type)
        return (
            0 if self.device_counts is None or api_device_type is None else getattr(self.device_counts, api_device_type)
        )

    def has_device(self, device_type: SectionPrefix, /) -> bool:
        """Return True if the control unit has at least one device of the device type."""
        if device_type == SectionPrefix.SYSTEM:
            return True

        if device_type == SectionPrefix.PHOTOVOLTAICS:
            return self.has_photovoltaics()

        return self.device_count(device_type) > 0

    def has_photovoltaics(self) -> bool:
        """Return True if the control unit has photovoltaics."""
        return self._get_configuration(SectionPrefix.SYSTEM, "has_photovoltaics") is True

    def _get_configuration(self, device_type: SectionPrefix, key: str, /, *, index: int | None = None) -> Value | None:
        """Return a value of the configuration that is read once on setup, of the device with the index."""
        readings: list[Reading] = self.configuration.get(device_type, {}).get(key, [])
        return readings[index or 0].value if len(readings) > (index or 0) else None

    def has_electrical_energy_meter(self, *, index: int | None = None) -> bool:
        """Return True if the heat pump has an electrical energy meter."""
        value: Value | None = self._get_configuration(
            SectionPrefix.HEAT_PUMP, "electrical_energy_meter_type", index=index
        )
        return isinstance(value, ElectricalEnergyMeterType) and value is not ElectricalEnergyMeterType.NONE

    def has_heat_meter(self, *, index: int | None = None) -> bool:
        """Return True if the heat pump has a heat meter."""
        value: Value | None = self._get_configuration(SectionPrefix.HEAT_PUMP, "heat_meter_type", index=index)
        return isinstance(value, HeatMeterType) and value is not HeatMeterType.NONE

    def has_active_cooling(self, *, index: int | None = None) -> bool:
        """Return True if the heat pump supports active cooling."""
        return self._get_configuration(SectionPrefix.HEAT_PUMP, "has_active_cooling", index=index) is True

    def has_passive_cooling(self, *, index: int | None = None) -> bool:
        """Return True if the heat pump supports passive cooling."""
        return self._get_configuration(SectionPrefix.HEAT_PUMP, "has_passive_cooling", index=index) is True

    def has_cooling(self, *, index: int | None = None) -> bool:
        """Return True if the heat pump supports active or passive cooling."""
        return self.has_active_cooling(index=index) or self.has_passive_cooling(index=index)

    def has_emissions(self, *, index: int | None = None) -> bool:
        """Return True if the external heat source has emissions."""
        return self._get_configuration(SectionPrefix.EXTERNAL_HEAT_SOURCE, "has_emissions", index=index) is True

    def has_cooling_heat_pump(self) -> bool:
        """Return True if any heat pump supports active or passive cooling."""
        return any(self.has_cooling(index=index) for index in range(self.device_count(SectionPrefix.HEAT_PUMP)))

    def has_cooling_circuit(self) -> bool:
        """Return True if any heating circuit cools."""
        # Some KEBA KeEnergy software versions do not have the configuration for active and passive cooling.
        # Cooling support can only be detected with the heating circuit mode.
        return any(
            self.is_cooling_circuit(index=index) for index in range(self.device_count(SectionPrefix.HEATING_CIRCUIT))
        )

    def is_cooling_circuit(self, *, index: int | None = None) -> bool:
        """Return True if the heating circuit cools, also if it heats as well."""
        return self._get_configuration(SectionPrefix.HEATING_CIRCUIT, "mode", index=index) in (
            HeatingCircuitType.COOLING,
            HeatingCircuitType.HEATING_AND_COOLING,
            HeatingCircuitType.HEATING_AND_ACTIVE_COOLING,
        )

    def is_heating_circuit(self, *, index: int | None = None) -> bool:
        """Return True if the heating circuit heats, also if it cools as well."""
        return self._get_configuration(SectionPrefix.HEATING_CIRCUIT, "mode", index=index) in (
            HeatingCircuitType.HEATING,
            HeatingCircuitType.HEATING_AND_COOLING,
            HeatingCircuitType.HEATING_AND_ACTIVE_COOLING,
        )

    def is_sensor_in_use(
        self, device_type: SectionPrefix, key: str, /, *, index: int | None, value_index: int | None
    ) -> bool:
        """Return True if the control unit reports the sensor as in use (message ID 0) or has no message ID for it."""
        return self._get_message_id_kind(device_type, key, index=index, value_index=value_index) in (
            MessageIdKind.OK,
            None,
        )

    def _get_message_id_kind(
        self,
        device_type: SectionPrefix,
        key: str,
        /,
        *,
        index: int | None,
        value_index: int | None,
    ) -> MessageIdKind | None:
        """Return the kind of the message ID of a sensor, or None if the sensor has none."""
        reading: Reading | None = self.get_reading(device_type, key, index=index, value_index=value_index)
        return None if reading is None or reading.message_id is None else reading.message_id.kind

    def is_sensor_deactivated(
        self, device_type: SectionPrefix, key: str, /, *, index: int | None, value_index: int | None
    ) -> bool:
        """Return True if the control unit reports the sensor as deactivated (message ID 10), i.e. not configured."""
        return (
            self._get_message_id_kind(device_type, key, index=index, value_index=value_index)
            is MessageIdKind.DEACTIVATED
        )
