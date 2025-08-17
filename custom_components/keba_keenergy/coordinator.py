"""DataUpdateCoordinator for the KEBA KeEnergy integration."""
from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientError, ClientSession
from keba_keenergy_api import KebaKeEnergyAPI
from keba_keenergy_api.constants import (
    HeatCircuit,
    HeatPump,
    HotWaterTank,
    SectionPrefix,
    System,
)
from keba_keenergy_api.endpoints import Value, ValueResponse
from keba_keenergy_api.error import APIError

from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class KebaKeEnergyDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, ValueResponse]]
):
    """Class to manage fetching KEBA KeEnergy data API."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        host: str,
        ssl: bool,
    ) -> None:
        """Initialize."""
        self.api: KebaKeEnergyAPI = KebaKeEnergyAPI(host, ssl=ssl, session=session)
        self._api_device_info: dict[str, Any] = {}
        self._api_system_info: dict[str, Any] = {}

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL)
        )

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
                    HeatCircuit.DAY_TEMPERATURE,
                    HeatCircuit.DAY_TEMPERATURE_THRESHOLD,
                    HeatCircuit.HEAT_REQUEST,
                    HeatCircuit.HOLIDAY_TEMPERATURE,
                    HeatCircuit.NAME,
                    HeatCircuit.NIGHT_TEMPERATURE,
                    HeatCircuit.NIGHT_TEMPERATURE_THRESHOLD,
                    HeatCircuit.OPERATING_MODE,
                    HeatCircuit.TEMPERATURE,
                    HeatCircuit.TEMPERATURE_OFFSET,
                    HeatPump.CIRCULATION_PUMP,
                    HeatPump.COMPRESSOR,
                    HeatPump.COMPRESSOR_INPUT_TEMPERATURE,
                    HeatPump.COMPRESSOR_OUTPUT_TEMPERATURE,
                    HeatPump.HEAT_REQUEST,
                    HeatPump.HIGH_PRESSURE,
                    HeatPump.INFLOW_TEMPERATURE,
                    HeatPump.LOW_PRESSURE,
                    HeatPump.NAME,
                    HeatPump.REFLUX_TEMPERATURE,
                    HeatPump.SOURCE_INPUT_TEMPERATURE,
                    HeatPump.SOURCE_OUTPUT_TEMPERATURE,
                    HeatPump.STATE,
                    HotWaterTank.HEAT_REQUEST,
                    HotWaterTank.MAX_TEMPERATURE,
                    HotWaterTank.MIN_TEMPERATURE,
                    HotWaterTank.OPERATING_MODE,
                    HotWaterTank.TEMPERATURE,
                    System.HEAT_CIRCUIT_NUMBERS,
                    System.HEAT_PUMP_NUMBERS,
                    System.HOT_WATER_TANK_NUMBERS,
                    System.OUTDOOR_TEMPERATURE,
                ],
            )
        except (APIError, ClientError) as error:
            _LOGGER.debug(error)
            raise UpdateFailed(error) from error

        return response

    @property
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
    def heat_pump_names(self) -> list[Value]:
        """Return heat pump names."""
        _heat_pump_names: list[Value] = self.data[SectionPrefix.HEAT_PUMP]["name"]
        return _heat_pump_names

    @property
    def heat_circuit_numbers(self) -> int:
        """Return number of heat circuits."""
        return int(self.data[SectionPrefix.SYSTEM]["heat_circuit_numbers"]["value"])

    @property
    def hot_water_tank_numbers(self) -> int:
        """Return number of hot water tanks."""
        return int(self.data[SectionPrefix.SYSTEM]["hot_water_tank_numbers"]["value"])
