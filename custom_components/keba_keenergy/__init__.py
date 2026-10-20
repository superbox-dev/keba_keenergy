# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""The KEBA KeEnergy integration."""

from __future__ import annotations

import logging
import socket
from typing import TYPE_CHECKING
from typing import Final

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .const import MANUFACTURER
from .const import PLATFORMS
from .coordinator import KebaKeEnergyConfigEntry
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .coordinator import get_device_identifier
from .services import async_setup_services

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceEntry
    from homeassistant.helpers.typing import ConfigType

CONFIG_SCHEMA: Final = cv.config_entry_only_config_schema(DOMAIN)


_LOGGER: Final = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # noqa: ARG001
    """Set up the  KEBA KeEnergy component."""
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: KebaKeEnergyConfigEntry) -> bool:
    """Set up the KEBA KeEnergy platform."""
    # Newer software versions of the Web HMI comes with self-signed SSL certificates.
    session: ClientSession = async_get_clientsession(hass, verify_ssl=False, family=socket.AF_INET)

    coordinator: KebaKeEnergyDataUpdateCoordinator = KebaKeEnergyDataUpdateCoordinator(
        hass,
        entry,
        session=session,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Register the control unit before other devices use it as `via_device`.
    device_registry: dr.DeviceRegistry = dr.async_get(hass)

    control_unit: DeviceEntry = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, get_device_identifier(entry.unique_id, SectionPrefix.SYSTEM, None))},
        manufacturer=MANUFACTURER,
        name=coordinator.name,
        model=coordinator.device_model,
        sw_version=coordinator.device_hmi_sw_version,
        serial_number=coordinator.device_serial_number,
    )

    coordinator.control_unit_device_id = control_unit.id

    # Remove the devices that the control unit no longer provides, e.g. a removed buffer tank.
    device_identifiers: set[str] = coordinator.device_identifiers()

    for device in dr.async_entries_for_config_entry(device_registry, entry.entry_id):
        if not any(domain == DOMAIN and identifier in device_identifiers for domain, identifier in device.identifiers):
            _LOGGER.debug("Remove stale device %s", device.identifiers)
            device_registry.async_remove_device(device.id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: KebaKeEnergyConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
