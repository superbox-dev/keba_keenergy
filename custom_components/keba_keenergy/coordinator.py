"""DataUpdateCoordinator for the KEBA KeEnergy integration."""

import logging
from asyncio import Lock
from copy import deepcopy
from datetime import date
from datetime import timedelta
from functools import cached_property
from typing import Any
from typing import cast
from zoneinfo import ZoneInfo

from aiohttp import ClientSession
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util.dt import now
from keba_keenergy_api.api import KebaKeEnergyAPI
from keba_keenergy_api.constants import BufferTank
from keba_keenergy_api.constants import ExternalHeatSource
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatPump
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import Photovoltaic
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import SolarCircuit
from keba_keenergy_api.constants import SwitchValve
from keba_keenergy_api.constants import System
from keba_keenergy_api.endpoints import Position
from keba_keenergy_api.endpoints import Value
from keba_keenergy_api.endpoints import ValueResponse
from keba_keenergy_api.error import APIError

from .const import DOMAIN
from .const import FLASH_WRITE_LIMIT_PER_WEEK
from .const import REQUEST_REFRESH_COOLDOWN
from .const import SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class KebaKeEnergyDataUpdateCoordinator(DataUpdateCoordinator[dict[str, ValueResponse]]):
    """Class to manage fetching KEBA KeEnergy data API."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        /,
        *,
        host: str,
        username: str | None,
        password: str | None,
        ssl: bool,
        session: ClientSession,
    ) -> None:
        """Initialize."""
        self._store: Store[dict[str, Any]] = Store(hass, version=1, key=DOMAIN)
        self._write_lock: Lock = Lock()

        self.api: KebaKeEnergyAPI = KebaKeEnergyAPI(
            host,
            username=username,
            password=password,
            ssl=ssl,
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
        self._has_photovoltaics: bool = False

        self.request_data: list[Section] = [
            ExternalHeatSource.OPERATING_MODE,
            ExternalHeatSource.TARGET_TEMPERATURE,
            ExternalHeatSource.HEAT_REQUEST,
            ExternalHeatSource.OPERATING_TIME,
            ExternalHeatSource.MAX_RUNTIME,
            ExternalHeatSource.ACTIVATION_COUNTER,
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
            HeatCircuit.TARGET_TEMPERATURE_NIGHT,
            HeatCircuit.HEATING_LIMIT_NIGHT,
            HeatCircuit.OPERATING_MODE,
            HeatCircuit.SELECTED_TARGET_TEMPERATURE,
            HeatCircuit.TARGET_TEMPERATURE,
            HeatCircuit.TARGET_TEMPERATURE_OFFSET,
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
            HeatPump.CIRCULATION_PUMP,
            HeatPump.SOURCE_PUMP_SPEED,
            HeatPump.COMPRESSOR,
            HeatPump.COMPRESSOR_NIGHT_SPEED,
            HeatPump.COMPRESSOR_INPUT_TEMPERATURE,
            HeatPump.COMPRESSOR_OUTPUT_TEMPERATURE,
            HeatPump.COMPRESSOR_USE_NIGHT_SPEED,
            HeatPump.CONDENSER_TEMPERATURE,
            HeatPump.VAPORIZER_TEMPERATURE,
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
            HeatPump.OPERATING_TIME,
            HeatPump.MAX_RUNTIME,
            HeatPump.ACTIVATION_COUNTER,
            HeatPump.HAS_COMPRESSOR_FAILURE,
            HeatPump.HAS_SOURCE_FAILURE,
            HeatPump.HAS_SOURCE_ACTUATOR_FAILURE,
            HeatPump.HAS_THREE_PHASE_FAILURE,
            HeatPump.HAS_SOURCE_PRESSURE_FAILURE,
            HeatPump.HAS_VFD_FAILURE,
            BufferTank.CURRENT_TOP_TEMPERATURE,
            BufferTank.CURRENT_BOTTOM_TEMPERATURE,
            BufferTank.OPERATING_MODE,
            BufferTank.STANDBY_TEMPERATURE,
            BufferTank.TARGET_TEMPERATURE,
            BufferTank.HEAT_REQUEST,
            BufferTank.COOL_REQUEST,
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
            SwitchValve.POSITION,
            System.OUTDOOR_TEMPERATURE,
            System.OPERATING_MODE,
            System.CPU_USAGE,
            System.WEBVIEW_CPU_USAGE,
            System.WEBSERVER_CPU_USAGE,
            System.CONTROL_CPU_USAGE,
            System.RAM_USAGE,
            System.FREE_RAM,
        ]
        self.position: Position | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=REQUEST_REFRESH_COOLDOWN,
                immediate=True,
            ),
        )

    async def async_initialize(self) -> None:
        """Initialize values from API that never changed."""
        store_data: dict[str, Any] | None = await self._store.async_load()

        if store_data:
            counter: dict[str, Any] | None = store_data.get("flash_write_counter")

            if isinstance(counter, dict):
                self._write_count_week = tuple(counter["week"])
                self._weekly_write_count = counter["count"]

        try:
            self._api_device_info = await self.api.system.get_device_info()
            self._api_system_info = await self.api.system.get_info()
            self._api_hmi_info = await self.api.system.get_hmi_info()
            self.position = await self.api.system.get_positions()
            self.request_data = await self.api.filter_request(
                request=self.request_data,
                position=self.position,
            )

            self._fixed_data = await self.api.read_data(
                request=[
                    System.HAS_PHOTOVOLTAICS,
                    HeatCircuit.HAS_ROOM_TEMPERATURE,
                    HeatCircuit.HAS_ROOM_HUMIDITY,
                    HeatPump.HAS_PASSIVE_COOLING,
                ],
                position=self.position,
            )

        except APIError as error:
            _LOGGER.error(error)  # noqa: TRY400
            raise UpdateFailed(error) from error

    async def _async_update_data(self) -> dict[str, ValueResponse]:
        """Read all values from API to update coordinator data."""
        try:
            response: dict[str, ValueResponse] = await self.api.read_data(
                request=self.request_data,
                position=self.position,
            )
        except APIError as error:
            _LOGGER.error(error)  # noqa: TRY400
            raise UpdateFailed(error) from error

        return response

    def async_update_value(
        self,
        value: Any,
        /,
        *,
        section_id: str,
        section: Section,
        index: int,
        key_index: int | None,
    ) -> None:
        """Optimistically update a single value into coordinator data."""
        data: dict[str, ValueResponse] = deepcopy(self.data)
        key: str = section.name.lower()

        if section.value.human_readable:
            value = section.value.human_readable(value).name.lower()

        values: list[list[Value]] | list[Value] | Value = data[section_id][key]

        if isinstance(values, list):
            value_by_index: list[Value] | Value = values[index]

            if isinstance(value_by_index, list) and key_index is not None:
                value_by_index[key_index]["value"] = value
            elif isinstance(value_by_index, dict):
                value_by_index["value"] = value

        self.async_set_updated_data(data)

    async def async_write_data(self, request: dict[Section, Any], *, ignore_weekly_write_count: bool = False) -> None:
        """Write data to the NAND from the KEBA KeEnergy control unit."""
        async with self._write_lock:
            await self._async_reset_weekly_counter_if_needed()

            if not ignore_weekly_write_count:
                self._weekly_write_count += 1

                await self._store.async_save(
                    {
                        "flash_write_counter": {
                            "week": list(self._write_count_week) if self._write_count_week else [],
                            "count": self._weekly_write_count,
                        },
                    },
                )

            _LOGGER.debug(
                "API write request %s (writes this week: %s)",
                request,
                self._weekly_write_count,
            )

            if self._weekly_write_count > FLASH_WRITE_LIMIT_PER_WEEK and not self._flash_issue_active:
                self._flash_issue_active = True
                self._create_issue()

        try:
            await self.api.write_data(request=request)
        except APIError as error:
            msg: str = f"Failed to update: {error}"
            raise HomeAssistantError(msg) from error

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

    async def _async_reset_weekly_counter_if_needed(self) -> None:
        today: date = now().date()
        current_week: tuple[int, int] = today.isocalendar().year, today.isocalendar().week

        if self._write_count_week != current_week:
            self._write_count_week = current_week
            self._weekly_write_count = 0
            self._flash_issue_active = False

            ir.async_delete_issue(
                self.hass,
                domain=DOMAIN,
                issue_id="frequent_flash_writes",
            )

            await self._store.async_save(
                {
                    "flash_write_counter": {
                        "week": list(self._write_count_week),
                        "count": self._weekly_write_count,
                    },
                },
            )

    async def get_timezone(self) -> ZoneInfo:
        """Get the timezone from the Web HMI."""
        timezone: str = await self.api.system.get_timezone()
        return ZoneInfo(timezone)

    async def set_away_date_range(self, *, start_timestamp: float, end_timestamp: float) -> None:
        """Set the away date range."""
        if self.position:
            await self.async_write_data(
                request={
                    HeatCircuit.AWAY_START_DATE: [int(start_timestamp) for _ in range(self.position.heat_circuit)],
                    HeatCircuit.AWAY_END_DATE: [int(end_timestamp) for _ in range(self.position.heat_circuit)],
                },
            )

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
        return cast("list[Value]", self.data[SectionPrefix.HEAT_PUMP]["name"])

    @cached_property
    def heat_circuit_numbers(self) -> int:
        """Return number of heat circuits."""
        return self.position.heat_circuit if self.position else 0

    @cached_property
    def solar_circuit_numbers(self) -> int:
        """Return number of solar circuits."""
        return self.position.solar_circuit if self.position else 0

    @cached_property
    def heat_pump_numbers(self) -> int:
        """Return number of heat pumps."""
        return self.position.heat_pump if self.position else 0

    @cached_property
    def buffer_tank_numbers(self) -> int:
        """Return number of buffer tanks."""
        return self.position.buffer_tank if self.position else 0

    @cached_property
    def hot_water_tank_numbers(self) -> int:
        """Return number of hot water tanks."""
        return self.position.hot_water_tank if self.position else 0

    @cached_property
    def external_heat_source_numbers(self) -> int:
        """Return number of external heat sources."""
        return self.position.external_heat_source if self.position else 0

    @cached_property
    def has_photovoltaics(self) -> str:
        """Check if photovoltaics is available."""
        data: Value = cast("Value", self._fixed_data[SectionPrefix.SYSTEM]["has_photovoltaics"])
        return str(data["value"])

    def has_room_temperature(self, *, index: int) -> str:
        """Check if room temperature sensor is available."""
        data: list[Value] = cast("list[Value]", self._fixed_data[SectionPrefix.HEAT_CIRCUIT]["has_room_temperature"])
        return str(data[index]["value"])

    def has_room_humidity(self, *, index: int) -> str:
        """Check if room humidity sensor is available."""
        data: list[Value] = cast("list[Value]", self._fixed_data[SectionPrefix.HEAT_CIRCUIT]["has_room_humidity"])
        return str(data[index]["value"])

    def has_passive_cooling(self, *, index: int) -> str:
        """Check if passive cooling is available."""
        data: list[Value] = cast("list[Value]", self._fixed_data[SectionPrefix.HEAT_PUMP]["has_passive_cooling"])
        return str(data[index]["value"])
