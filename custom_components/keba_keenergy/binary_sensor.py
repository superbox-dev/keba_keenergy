# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Support for KEBA KeEnergy binary sensors."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Final

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.const import EntityCategory

from .const import RemoteAccessValue
from .const import SectionPrefix
from .entity import KebaKeEnergyEntity
from .entity import KebaKeEnergyEntityDescription
from .entity import KebaKeEnergyRemoteAccessEntity
from .entity import async_setup_data_entities
from .entity import async_setup_remote_access_entities
from .entity import has_photovoltaics

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .coordinator import KebaKeEnergyConfigEntry


_LOGGER: Final = logging.getLogger(__name__)

PARALLEL_UPDATES: Final[int] = 0


@dataclass(frozen=True, kw_only=True)
class KebaKeEnergyBinarySensorEntityDescription(
    BinarySensorEntityDescription,
    KebaKeEnergyEntityDescription,
):
    """Class describing KEBA KeEnergy binary sensor entities."""


class KebaKeEnergyBinarySensorEntity(KebaKeEnergyEntity, BinarySensorEntity):
    """KEBA KeEnergy binary sensor entity."""

    entity_description: KebaKeEnergyBinarySensorEntityDescription
    _platform_domain: str = BINARY_SENSOR_DOMAIN

    @property
    def is_on(self) -> bool | None:
        """Return True if the binary sensor is on, None if the value is missing."""
        return self.get_typed_value(self._data_key, bool)


class KebaKeEnergyRemoteAccessBinarySensorEntity(KebaKeEnergyRemoteAccessEntity, BinarySensorEntity):
    """KEBA KeEnergy binary sensor of the remote access (remote maintenance)."""

    _platform_domain: str = BINARY_SENSOR_DOMAIN


BINARY_SENSOR_TYPES: Final[dict[SectionPrefix, tuple[KebaKeEnergyBinarySensorEntityDescription, ...]]] = {
    SectionPrefix.SOLAR_CIRCUIT: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            value_index=0,
            translation_key="solar_circuit_heat_request",
            translation_placeholders={
                "counter": " 1",
            },
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            value_index=1,
            translation_key="solar_circuit_heat_request",
            translation_placeholders={
                "counter": " 2",
            },
        ),
    ),
    SectionPrefix.HEATING_CIRCUIT: (
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.RUNNING,
            entity_registry_enabled_default=False,
            key="pump_state",
            translation_key="heating_circuit_pump_state",
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        KebaKeEnergyBinarySensorEntityDescription(
            condition=has_photovoltaics,
            key="consuming_excess_energy",
            translation_key="heat_pump_consuming_excess_energy",
            icon="mdi:solar-power",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            translation_key="heat_pump_request",
            translation_placeholders={
                "counter": "",
            },
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_compressor_failure",
            translation_key="heat_pump_compressor_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_source_failure",
            translation_key="heat_pump_source_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_source_actuator_failure",
            translation_key="heat_pump_source_actuator_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_three_phase_failure",
            translation_key="heat_pump_three_phase_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_source_pressure_failure",
            translation_key="heat_pump_source_pressure_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_vfd_failure",
            translation_key="heat_pump_vfd_failure",
        ),
    ),
    SectionPrefix.BUFFER_TANK: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            translation_key="buffer_tank_heat_request",
            translation_placeholders={
                "counter": "",
            },
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="cool_request",
            translation_key="buffer_tank_cool_request",
            translation_placeholders={
                "counter": "",
            },
        ),
    ),
    SectionPrefix.DHW_TANK: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            translation_key="dhw_tank_heat_request",
            translation_placeholders={
                "counter": "",
            },
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="hot_water_flow",
            new_key="fresh_water_flow",
            translation_key="dhw_tank_hot_water_flow",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.RUNNING,
            entity_registry_enabled_default=False,
            key="circulation_pump_state",
            translation_key="dhw_tank_circulation_pump_state",
        ),
    ),
    SectionPrefix.EXTERNAL_HEAT_SOURCE: (
        KebaKeEnergyBinarySensorEntityDescription(
            condition=has_photovoltaics,
            key="consuming_excess_energy",
            translation_key="external_heat_source_consuming_excess_energy",
            icon="mdi:solar-power",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            translation_key="external_heat_source_heat_request",
            translation_placeholders={
                "counter": "",
            },
        ),
    ),
    SectionPrefix.PHOTOVOLTAICS: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="excess_energy_active",
            translation_key="photovoltaics_excess_energy",
        ),
    ),
}

REMOTE_ACCESS_BINARY_SENSOR_TYPES: Final[tuple[BinarySensorEntityDescription, ...]] = (
    BinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        key=RemoteAccessValue.REMOTE_MAINTENANCE_CONNECTED,
        translation_key="system_remote_maintenance_connected",
    ),
    BinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        key=RemoteAccessValue.REMOTE_MAINTENANCE_SERVER_REACHABLE,
        translation_key="system_remote_maintenance_server_reachable",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy binary sensors from a config entry."""
    async_setup_data_entities(
        entry,
        async_add_entities,
        BINARY_SENSOR_TYPES,
        KebaKeEnergyBinarySensorEntity,
        "binary sensor",
    )
    async_setup_remote_access_entities(
        entry,
        async_add_entities,
        REMOTE_ACCESS_BINARY_SENSOR_TYPES,
        KebaKeEnergyRemoteAccessBinarySensorEntity,
    )
