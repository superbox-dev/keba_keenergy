"""DataUpdateCoordinator for the KEBA KeEnergy integration."""

import logging
from datetime import timedelta
from functools import cached_property
from typing import Any
from typing import cast

from aiohttp import ClientSession
from homeassistant.core import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
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
from keba_keenergy_api.constants import System
from keba_keenergy_api.endpoints import Position
from keba_keenergy_api.endpoints import Value
from keba_keenergy_api.endpoints import ValueResponse
from keba_keenergy_api.error import APIError

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

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL))

    async def async_initialize(self) -> None:
        """Initialize values from API that never changed."""
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
