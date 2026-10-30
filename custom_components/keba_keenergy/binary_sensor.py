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

from .const import SectionPrefix
from .entity import KebaKeEnergyEntity
from .entity import KebaKeEnergyEntityDescription
from .entity import async_setup_entities

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import KebaKeEnergyConfigEntry


_LOGGER: Final = logging.getLogger(__name__)

PARALLEL_UPDATES: Final[int] = 0


@dataclass(frozen=True, kw_only=True)
class KebaKeEnergyBinarySensorEntityDescription(
    BinarySensorEntityDescription,
    KebaKeEnergyEntityDescription,
):
    """Class describing KEBA KeEnergy binary sensor entities."""


BINARY_SENSOR_TYPES: Final[dict[SectionPrefix, tuple[KebaKeEnergyBinarySensorEntityDescription, ...]]] = {
    SectionPrefix.SOLAR_CIRCUIT: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            value_index=0,
            translation_key="heat_request",
            translation_placeholders={
                "counter": " 1",
            },
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            value_index=1,
            translation_key="heat_request",
            translation_placeholders={
                "counter": " 2",
            },
        ),
    ),
    SectionPrefix.HEAT_CIRCUIT: (
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.RUNNING,
            entity_registry_enabled_default=False,
            key="pump_state",
            translation_key="pump_state",
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        KebaKeEnergyBinarySensorEntityDescription(
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            key="consuming_excess_energy",
            translation_key="consuming_excess_energy",
            icon="mdi:solar-power",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            translation_key="heat_request",
            translation_placeholders={
                "counter": "",
            },
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_compressor_failure",
            translation_key="compressor_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_source_failure",
            translation_key="source_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_source_actuator_failure",
            translation_key="source_actuator_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_three_phase_failure",
            translation_key="three_phase_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_source_pressure_failure",
            translation_key="source_pressure_failure",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_vfd_failure",
            translation_key="vfd_failure",
        ),
    ),
    SectionPrefix.BUFFER_TANK: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            translation_key="heat_request",
            translation_placeholders={
                "counter": "",
            },
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="cool_request",
            translation_key="cool_request",
            translation_placeholders={
                "counter": "",
            },
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            translation_key="heat_request",
            translation_placeholders={
                "counter": "",
            },
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="hot_water_flow",
            new_key="fresh_water_flow",
            translation_key="hot_water_flow",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.RUNNING,
            entity_registry_enabled_default=False,
            key="circulation_pump_state",
            translation_key="circulation_pump_state",
        ),
    ),
    SectionPrefix.EXTERNAL_HEAT_SOURCE: (
        KebaKeEnergyBinarySensorEntityDescription(
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            key="consuming_excess_energy",
            translation_key="consuming_excess_energy",
            icon="mdi:solar-power",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            translation_key="heat_request",
            translation_placeholders={
                "counter": "",
            },
        ),
    ),
    SectionPrefix.PHOTOVOLTAICS: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="excess_energy_active",
            translation_key="excess_energy",
        ),
    ),
}


class KebaKeEnergyBinarySensorEntity(KebaKeEnergyEntity, BinarySensorEntity):
    """KEBA KeEnergy binary sensor entity."""

    entity_description: KebaKeEnergyBinarySensorEntityDescription
    _platform_domain: str = BINARY_SENSOR_DOMAIN

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.get_typed_value(self._data_key, bool)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy binary sensors from a config entry."""
    async_setup_entities(
        entry,
        async_add_entities,
        BINARY_SENSOR_TYPES,
        KebaKeEnergyBinarySensorEntity,
        "binary sensor",
    )
