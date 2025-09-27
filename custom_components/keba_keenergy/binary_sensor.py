"""Support for KEBA KeEnergy binary sensors."""

import logging
from typing import cast

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyExtendedEntity

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_TYPES: dict[str, tuple[BinarySensorEntityDescription, ...]] = {
    SectionPrefix.HOT_WATER_TANK: (
        BinarySensorEntityDescription(
            key="heat_request",
            translation_key="heat_request",
            icon="mdi:fire",
        ),
        BinarySensorEntityDescription(
            key="hot_water_flow",
            translation_key="hot_water_flow",
            icon="mdi:water",
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        BinarySensorEntityDescription(
            key="heat_request",
            translation_key="heat_request",
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
    # e.g. hot water tank, heat circuit or heat pump.
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
        description: BinarySensorEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: BinarySensorEntityDescription = description
        super().__init__(coordinator, entry=entry, section_id=section_id, index=index)
        self.entity_id: str = f"{BINARY_SENSOR_DOMAIN}.{DOMAIN}_{self.unique_id}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return cast("bool", (self.get_value(self.entity_description.key) == "on"))
