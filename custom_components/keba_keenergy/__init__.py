"""The KEBA KeEnergy integration."""

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_SSL
from homeassistant.const import CONF_USERNAME
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .const import MANUFACTURER
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .services import async_setup_services

if TYPE_CHECKING:
    from aiohttp import ClientSession

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up KEBA KeEnergy platform."""
    host: str = entry.data[CONF_HOST]
    username: str | None = entry.data.get(CONF_USERNAME)
    password: str | None = entry.data.get(CONF_PASSWORD)
    ssl: bool = entry.data[CONF_SSL]

    # Newer software versions of the Web HMI comes with self-signed SSL certificates
    session: ClientSession = async_get_clientsession(hass, verify_ssl=False)

    coordinator: KebaKeEnergyDataUpdateCoordinator = KebaKeEnergyDataUpdateCoordinator(
        hass,
        host=host,
        username=username,
        password=password,
        ssl=ssl,
        session=session,
    )

    await coordinator.async_initialize()
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # register keba_keenergy before via_device is used
    device_registry = dr.async_get(hass)

    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{entry.unique_id}_{DOMAIN}")},
        manufacturer=MANUFACTURER,
        name=coordinator.name,
        model=coordinator.device_model,
        sw_version=coordinator.device_hmi_sw_version,
        serial_number=coordinator.device_serial_number,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
