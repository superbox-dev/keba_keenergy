"""Support for KEBA KeEnergy binary sensors."""

import logging
from dataclasses import dataclass
from typing import cast

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyExtendedEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class KebaKeEnergyBinarySensorEntityDescriptionMixin:
    """Required values for KEBA KeEnergy binary sensors."""

    key_index: int | None


@dataclass(frozen=True)
class KebaKeEnergyBinarySensorEntityDescription(
    BinarySensorEntityDescription,
    KebaKeEnergyBinarySensorEntityDescriptionMixin,
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
            icon="mdi:fire",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            key_index=1,
            translation_key="heat_request",
            translation_placeholders={
                "counter": " 2",
            },
            icon="mdi:fire",
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            key_index=None,
            translation_key="heat_request",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:fire",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_compressor_failure",
            key_index=None,
            translation_key="compressor_failure",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:alert-rhombus",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_source_failure",
            key_index=None,
            translation_key="source_failure",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:alert-rhombus",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_source_actuator_failure",
            key_index=None,
            translation_key="source_actuator_failure",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:alert-rhombus",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_three_phase_failure",
            key_index=None,
            translation_key="three_phase_failure",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:alert-rhombus",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_source_pressure_failure",
            key_index=None,
            translation_key="source_pressure_failure",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:alert-rhombus",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="has_vfd_failure",
            key_index=None,
            translation_key="vfd_failure",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:alert-rhombus",
        ),
    ),
    SectionPrefix.BUFFER_TANK: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            key_index=None,
            translation_key="heat_request",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:fire",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="cool_request",
            key_index=None,
            translation_key="cool_request",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:snowflake",
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            key_index=None,
            translation_key="heat_request",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:fire",
        ),
        KebaKeEnergyBinarySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="hot_water_flow",
            key_index=None,
            translation_key="hot_water_flow",
            icon="mdi:water",
        ),
    ),
    SectionPrefix.EXTERNAL_HEAT_SOURCE: (
        KebaKeEnergyBinarySensorEntityDescription(
            key="heat_request",
            key_index=None,
            translation_key="heat_request",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:fire",
        ),
    ),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up KEBA KeEnergy binary sensors from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    binary_sensors: list[KebaKeEnergyBinarySensorEntity] = []

    # Loop over all device data and add an index to the binary sensor
    # if there is more than one device of the same type
    # e.g. buffer tank, hot water tank, heat circuit, solar circuit or heat pump.

    for section_id, section_data in coordinator.data.items():
        for description in BINARY_SENSOR_TYPES.get(section_id, {}):
            for key, values in section_data.items():
                if key == description.key:
                    device_numbers: int = len(values) if isinstance(values, list) else 1
                    binary_sensors += [
                        KebaKeEnergyBinarySensorEntity(
                            coordinator,
                            description=description,
                            entry=entry,
                            section_id=section_id,
                            index=index if device_numbers > 1 else None,
                        )
                        for index in range(device_numbers)
                    ]

    async_add_entities(binary_sensors)


class KebaKeEnergyBinarySensorEntity(KebaKeEnergyExtendedEntity, BinarySensorEntity):
    """KEBA KeEnergy sensor entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: KebaKeEnergyBinarySensorEntityDescription,
        entry: ConfigEntry,
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
        return cast("bool", (self.get_value(self.entity_description.key) == "on"))
