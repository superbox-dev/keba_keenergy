"""Support for KEBA KeEnergy binary sensors."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.const import EntityCategory
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .entity import KebaKeEnergyEntity
from .entity import KebaKeEnergyEntityDescriptionMixin

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES: Final[int] = 0


@dataclass(frozen=True, kw_only=True)
class KebaKeEnergyBinarySensorEntityDescription(
    BinarySensorEntityDescription,
    KebaKeEnergyEntityDescriptionMixin,
):
    """Class describing KEBA KeEnergy binary sensor entities."""


BINARY_SENSOR_TYPES: dict[str, tuple[KebaKeEnergyBinarySensorEntityDescription, ...]] = {
    SectionPrefix.SOLAR_CIRCUIT: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            key_index=0,
            translation_key="heat_request",
            translation_placeholders={
                "counter": " 1",
            },
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            key_index=1,
            translation_key="heat_request",
            translation_placeholders={
                "counter": " 2",
            },
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        KebaKeEnergyBinarySensorEntityDescription(
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            key="consuming_excess_energy",
            translation_key="excess_energy",
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
            condition=lambda coordinator, index: coordinator.has_fresh_water_module(index=index),
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
            translation_key="excess_energy",
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
            translation_key="pv_excess_energy",
        ),
    ),
}


class KebaKeEnergyBinarySensorEntity(KebaKeEnergyEntity, BinarySensorEntity):
    """KEBA KeEnergy sensor entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: KebaKeEnergyBinarySensorEntityDescription,
        entry: KebaKeEnergyConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: KebaKeEnergyBinarySensorEntityDescription = description

        super().__init__(
            coordinator,
            entry=entry,
            section_id=section_id,
            index=index,
            key_index=self.entity_description.key_index,
        )

        self.entity_id: str = f"{BINARY_SENSOR_DOMAIN}.{DOMAIN}_{self.unique_id}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.get_value(self.entity_description.new_key or self.entity_description.key, expected_type=str) == "on"


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy binary sensors from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data
    binary_sensors: list[KebaKeEnergyBinarySensorEntity] = []

    # Loop over all device data and add an index to the binary sensor
    # if there is more than one device of the same type
    # e.g. buffer tank, hot water tank, heat circuit, solar circuit or heat pump.

    for section_id, section_data in coordinator.data.items():
        for description in BINARY_SENSOR_TYPES.get(section_id, ()):
            for key, values in section_data.items():
                if key in [description.key, description.new_key]:
                    device_numbers: int = len(values) if isinstance(values, list) else 1

                    for index in range(device_numbers):
                        if description.condition is not None and not description.condition(coordinator, index):
                            continue

                        binary_sensors += [
                            KebaKeEnergyBinarySensorEntity(
                                coordinator,
                                description=description,
                                entry=entry,
                                section_id=section_id,
                                index=index if device_numbers > 1 else None,
                            ),
                        ]

    async_add_entities(binary_sensors)
