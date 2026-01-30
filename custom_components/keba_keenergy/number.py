"""Support for the KEBA KeEnergy numbers."""

import logging
from dataclasses import dataclass
from functools import cached_property

from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.number import NumberEntity
from homeassistant.components.number import NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyExtendedEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class KebaKeEnergyNumberEntityDescriptionMixin:
    """Required values for KEBA KeEnergy sensors."""

    key_index: int | None
    scale: int


@dataclass(frozen=True)
class KebaKeEnergyNumberEntityDescription(
    NumberEntityDescription,
    KebaKeEnergyNumberEntityDescriptionMixin,
):
    """Class describing KEBA KeEnergy number entities."""


NUMBER_TYPES: dict[str, tuple[KebaKeEnergyNumberEntityDescription, ...]] = {
    SectionPrefix.HEAT_CIRCUIT: (
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="target_temperature_day",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_temperature_day",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="target_temperature_night",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_temperature_night",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="target_temperature_away",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_temperature_away",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="target_temperature_offset",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_temperature_offset",
            scale=1,
        ),
    ),
    SectionPrefix.SOLAR_CIRCUIT: (
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="target_temperature",
            key_index=0,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": " 1",
            },
            icon="mdi:thermometer-water",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="target_temperature",
            key_index=1,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": " 2",
            },
            icon="mdi:thermometer-water",
            scale=1,
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.SPEED,
            entity_registry_enabled_default=False,
            key="compressor_night_speed",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            native_step=1,
            translation_key="compressor_night_speed",
            scale=100,
        ),
    ),
    SectionPrefix.BUFFER_TANK: (
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="standby_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
            scale=1,
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="standby_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="target_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-chevron-up",
            scale=1,
        ),
    ),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up KEBA KeEnergy numbers from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    numbers: list[KebaKeEnergyNumberEntity] = []

    # Loop over all device data and add an index to the sensor
    # if there is more than one device of the same type
    # e.g. buffer tank, hot water tank, heat circuit, solar circuit or heat pump.

    for section_id, section_data in coordinator.data.items():
        for description in NUMBER_TYPES.get(section_id, {}):
            for key, values in section_data.items():
                if key == description.key:
                    device_numbers: int = len(values) if isinstance(values, list) else 1
                    numbers += [
                        KebaKeEnergyNumberEntity(
                            coordinator,
                            description=description,
                            entry=entry,
                            section_id=section_id,
                            index=index if device_numbers > 1 else None,
                        )
                        for index in range(device_numbers)
                    ]

    async_add_entities(numbers)


class KebaKeEnergyNumberEntity(KebaKeEnergyExtendedEntity, NumberEntity):
    """KEBA KeEnergy number entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: KebaKeEnergyNumberEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: KebaKeEnergyNumberEntityDescription = description

        super().__init__(
            coordinator,
            entry=entry,
            section_id=section_id,
            index=index,
            key_index=self.entity_description.key_index,
        )

        self.entity_id: str = f"{NUMBER_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @cached_property
    def native_min_value(self) -> float:
        """Return the maximum value."""
        return (
            float(self.get_attribute(self.entity_description.key, attr="lower_limit")) * self.entity_description.scale
        )

    @cached_property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return (
            float(self.get_attribute(self.entity_description.key, attr="upper_limit")) * self.entity_description.scale
        )

    @property
    def native_value(self) -> float:
        """Return the state of the number."""
        return float(self.get_value(self.entity_description.key)) * self.entity_description.scale

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self._async_write_data(
            value / self.entity_description.scale,
            section=self.section,
            device_numbers=self.device_numbers,
        )
