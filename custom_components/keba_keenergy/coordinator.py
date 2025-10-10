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
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatPump
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import System
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

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL))

    async def _async_update_data(self) -> dict[str, ValueResponse]:
        """Update coordinator data.

        Update data with device, system, heat pump, heat circuit
        and hot water tank data.
        """
        return await self.update_data()

    async def update_data(self) -> dict[str, ValueResponse]:
        """Read all values from API to update coordinator data."""
        try:
            self._api_device_info = await self.api.system.get_device_info()
            self._api_system_info = await self.api.system.get_info()

            response: dict[str, ValueResponse] = await self.api.read_data(
                request=[
                    HeatCircuit.HAS_ROOM_TEMPERATURE,
                    HeatCircuit.HAS_ROOM_HUMIDITY,
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
                    HeatCircuit.NAME,
                    HeatCircuit.TARGET_TEMPERATURE_NIGHT,
                    HeatCircuit.HEATING_LIMIT_NIGHT,
                    HeatCircuit.OPERATING_MODE,
                    HeatCircuit.TARGET_TEMPERATURE,
                    HeatCircuit.TARGET_TEMPERATURE_OFFSET,
                    HeatPump.CIRCULATION_PUMP,
                    HeatPump.COMPRESSOR,
                    HeatPump.COMPRESSOR_INPUT_TEMPERATURE,
                    HeatPump.COMPRESSOR_OUTPUT_TEMPERATURE,
                    HeatPump.HEAT_REQUEST,
                    HeatPump.HIGH_PRESSURE,
                    HeatPump.FLOW_TEMPERATURE,
                    HeatPump.LOW_PRESSURE,
                    HeatPump.NAME,
                    HeatPump.RETURN_FLOW_TEMPERATURE,
                    HeatPump.SOURCE_INPUT_TEMPERATURE,
                    HeatPump.SOURCE_OUTPUT_TEMPERATURE,
                    HeatPump.STATE,
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
                    HeatPump.HAS_PASSIVE_COOLING,
                    HotWaterTank.HEAT_REQUEST,
                    HotWaterTank.HOT_WATER_FLOW,
                    HotWaterTank.FRESH_WATER_MODULE_TEMPERATURE,
                    HotWaterTank.TARGET_TEMPERATURE,
                    HotWaterTank.STANDBY_TEMPERATURE,
                    HotWaterTank.OPERATING_MODE,
                    HotWaterTank.CURRENT_TEMPERATURE,
                    System.HEAT_CIRCUIT_NUMBERS,
                    System.HEAT_PUMP_NUMBERS,
                    System.HOT_WATER_TANK_NUMBERS,
                    System.EXTERNAL_HEAT_SOURCES_NUMBERS,
                    System.OUTDOOR_TEMPERATURE,
                    System.OPERATING_MODE,
                ],
            )
        except APIError as error:
            _LOGGER.error(error)  # noqa: TRY400
            raise UpdateFailed(error) from error

        return response

    @cached_property
    def configuration_url(self) -> str:
        """Return web gui url."""
        return str(self.api.device_url)

    @property
    def device_model(self) -> str:
        """Return device model name."""
        return str(self._api_device_info["name"])

    @property
    def device_name(self) -> str:
        """Return device name."""
        return str(self._api_system_info["name"])

    @property
    def device_sw_version(self) -> str:
        """Return software version."""
        return str(self._api_system_info["version"])

    @property
    def device_serial_number(self) -> str:
        """Return serial number."""
        return str(self._api_device_info["serNo"])

    @property
    def heat_pump_names(self) -> list[Value]:
        """Return heat pump names."""
        return cast("list[Value]", self.data[SectionPrefix.HEAT_PUMP]["name"])

    @property
    def heat_circuit_numbers(self) -> int:
        """Return number of heat circuits."""
        data: Value = cast("Value", self.data[SectionPrefix.SYSTEM]["heat_circuit_numbers"])
        return int(data["value"])

    @property
    def heat_pump_numbers(self) -> int:
        """Return number of heat pumps."""
        data: Value = cast("Value", self.data[SectionPrefix.SYSTEM]["heat_pump_numbers"])
        return int(data["value"])

    @property
    def hot_water_tank_numbers(self) -> int:
        """Return number of hot water tanks."""
        data: Value = cast("Value", self.data[SectionPrefix.SYSTEM]["hot_water_tank_numbers"])
        return int(data["value"])

    def has_room_temperature(self, *, index: int) -> str:
        """Check if room temperature sensor is available."""
        data: list[Value] = cast("list[Value]", self.data[SectionPrefix.HEAT_CIRCUIT]["has_room_temperature"])
        return str(data[index]["value"])

    def has_room_humidity(self, *, index: int) -> str:
        """Check if room humidity sensor is available."""
        data: list[Value] = cast("list[Value]", self.data[SectionPrefix.HEAT_CIRCUIT]["has_room_humidity"])
        return str(data[index]["value"])

    def has_passive_cooling(self, *, index: int) -> str:
        """Check if passive cooling is available."""
        data: list[Value] = cast("list[Value]", self.data[SectionPrefix.HEAT_PUMP]["has_passive_cooling"])
        return str(data[index]["value"])
