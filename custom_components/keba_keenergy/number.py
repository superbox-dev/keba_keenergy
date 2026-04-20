"""Support for the KEBA KeEnergy numbers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cached_property
from typing import Final
from typing import TYPE_CHECKING

from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.number import NumberEntity
from homeassistant.components.number import NumberEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.const import PERCENTAGE
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HassJob
from homeassistant.helpers.event import async_call_later
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .const import FLASH_WRITE_DELAY
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
class KebaKeEnergyNumberEntityDescription(
    NumberEntityDescription,
    KebaKeEnergyEntityDescriptionMixin,
):
    """Class describing KEBA KeEnergy number entities."""

    scale: int


class KebaKeEnergyNumberEntity(KebaKeEnergyEntity, NumberEntity):
    """KEBA KeEnergy number entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: KebaKeEnergyNumberEntityDescription,
        entry: KebaKeEnergyConfigEntry,
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

        self._pending_key = self.entity_description.key
        self._pending_section = self.section
        self._pending_device_numbers = self.device_numbers

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
    def native_value(self) -> float | None:
        """Return the state of the number."""
        native_value: float | None

        if self._pending_value is not None and self._async_call_later:
            native_value = self._pending_value * self.entity_description.scale
        else:
            native_value = self.get_value(self.entity_description.key, expected_type=float)

            if native_value:
                native_value = native_value * self.entity_description.scale

        return native_value

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self._pending_value = value / self.entity_description.scale

        if self._async_call_later:
            self._async_call_later()
            self._async_call_later = None

        self._async_call_later = async_call_later(
            hass=self.hass,
            delay=FLASH_WRITE_DELAY,
            action=HassJob(
                self._async_debounced_write_data,
                cancel_on_shutdown=True,
            ),
        )


NUMBER_TYPES: dict[str, tuple[KebaKeEnergyNumberEntityDescription, ...]] = {
    SectionPrefix.HEAT_CIRCUIT: (
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="target_temperature_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_temperature_day",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="target_cooling_temperature_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_cooling_temperature_day",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="heating_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="heating_limit_day",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="cooling_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="cooling_limit_day",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="target_temperature_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_temperature_night",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="target_cooling_temperature_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_cooling_temperature_night",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="heating_limit_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="heating_limit_night",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="cooling_limit_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="cooling_limit_night",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="target_temperature_away",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_temperature_away",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            key="target_temperature_offset",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_room_temperature_offset",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="heating_curve_offset",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.1,
            translation_key="heating_curve_offset",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="cooling_curve_offset",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.1,
            translation_key="cooling_curve_offset",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="heating_curve_slope",
            native_step=0.01,
            translation_key="heating_curve_slope",
            icon="mdi:slope-uphill",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="cooling_curve_slope",
            native_step=0.01,
            translation_key="cooling_curve_slope",
            icon="mdi:slope-uphill",
            scale=1,
        ),
    ),
    SectionPrefix.SOLAR_CIRCUIT: (
        KebaKeEnergyNumberEntityDescription(
            entity_category=EntityCategory.CONFIG,
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
            entity_category=EntityCategory.CONFIG,
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
            entity_category=EntityCategory.CONFIG,
            device_class=NumberDeviceClass.SPEED,
            entity_registry_enabled_default=False,
            key="compressor_night_speed",
            native_unit_of_measurement=PERCENTAGE,
            native_step=1,
            translation_key="compressor_night_speed",
            scale=100,
        ),
    ),
    SectionPrefix.BUFFER_TANK: (
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="excess_energy_target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="excess_energy_target_temperature",
            icon="mdi:thermometer-plus",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="excess_energy_target_temperature_hysteresis",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.1,
            translation_key="excess_energy_target_temperature_hysteresis",
            icon="mdi:thermometer",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            entity_category=EntityCategory.CONFIG,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="standby_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="outdoor_temperature_excess_energy_limit",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="outdoor_temperature_excess_energy_limit",
            icon="mdi:thermometer",
            scale=1,
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        KebaKeEnergyNumberEntityDescription(
            entity_category=EntityCategory.CONFIG,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="standby_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            entity_category=EntityCategory.CONFIG,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-chevron-up",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="excess_energy_target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="excess_energy_target_temperature",
            icon="mdi:thermometer-plus",
            scale=1,
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy numbers from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data
    numbers: list[KebaKeEnergyNumberEntity] = []

    # Loop over all device data and add an index to the sensor
    # if there is more than one device of the same type
    # e.g. buffer tank, hot water tank, heat circuit, solar circuit or heat pump.

    for section_id, section_data in coordinator.data.items():
        for description in NUMBER_TYPES.get(section_id, ()):
            for key, values in section_data.items():
                if key in [description.key, description.new_key]:
                    device_numbers: int = len(values) if isinstance(values, list) else 1

                    for index in range(device_numbers):
                        if description.condition is not None and not description.condition(coordinator, index):
                            continue

                        numbers += [
                            KebaKeEnergyNumberEntity(
                                coordinator,
                                description=description,
                                entry=entry,
                                section_id=section_id,
                                index=index if device_numbers > 1 else None,
                            ),
                        ]

    async_add_entities(numbers)
