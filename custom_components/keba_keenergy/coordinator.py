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
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.endpoints import Value
from keba_keenergy_api.endpoints import ValueResponse
from keba_keenergy_api.error import APIError

from .const import SCAN_INTERVAL
from .const import SUPPORTED_API_ENDPOINTS
from .helpers import compare_versions

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

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL))

    @cached_property
    def _supported_api_endpoints(self) -> list[Section]:
        request: list[Section] = []

        for supported_api_endpoint in (
            SUPPORTED_API_ENDPOINTS.get(self.device_model, []) + SUPPORTED_API_ENDPOINTS["ALL"]
        ):
            if supported_api_endpoint.min_version is None or (
                supported_api_endpoint.min_version
                and compare_versions(self.device_hmi_sw_version, supported_api_endpoint.min_version) == 1
            ):
                request.append(supported_api_endpoint.section)  # noqa: PERF401

        return request

    async def _async_update_data(self) -> dict[str, ValueResponse]:
        """Update coordinator data.

        Update data with device, system, heat pump, heat circuit
        and hot water tank data.
        """
        return await self.update_data()

    async def update_data(self) -> dict[str, ValueResponse]:
        """Read all values from API to update coordinator data."""
        try:
            if not self._api_device_info:
                self._api_device_info = await self.api.system.get_device_info()

            if not self._api_system_info:
                self._api_system_info = await self.api.system.get_info()

            if not self._api_hmi_info:
                self._api_hmi_info = await self.api.system.get_hmi_info()

            response: dict[str, ValueResponse] = await self.api.read_data(request=self._supported_api_endpoints)
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
    def device_hmi_sw_version(self) -> str:
        """Return HMI software version."""
        return str(self._api_hmi_info["name"].replace("KeEnergy.WebHmi_", ""))

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

    @property
    def external_heat_source_numbers(self) -> int:
        """Return number of external heat sources."""
        data: Value = cast("Value", self.data[SectionPrefix.SYSTEM]["external_heat_source_numbers"])
        return int(data["value"])

    def has_photovoltaics(self) -> str:
        """Check if photovoltaics is available."""
        data: Value = cast("Value", self.data[SectionPrefix.SYSTEM]["has_photovoltaics"])
        return str(data["value"])

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
