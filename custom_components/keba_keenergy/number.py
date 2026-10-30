# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Support for the KEBA KeEnergy numbers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Final

from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.number import NumberEntity
from homeassistant.components.number import NumberEntityDescription
from homeassistant.const import PERCENTAGE
from homeassistant.const import EntityCategory
from homeassistant.const import UnitOfTemperature
from homeassistant.const import UnitOfTime

from .const import DOMAIN
from .const import SectionPrefix
from .entity import KebaKeEnergyEntity
from .entity import KebaKeEnergyEntityDescription
from .entity import async_setup_entities

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator


_LOGGER: Final = logging.getLogger(__name__)

PARALLEL_UPDATES: Final[int] = 0


@dataclass(frozen=True, kw_only=True)
class KebaKeEnergyNumberEntityDescription(
    NumberEntityDescription,
    KebaKeEnergyEntityDescription,
):
    """Class describing KEBA KeEnergy number entities."""

    scale: float


class KebaKeEnergyNumberEntity(KebaKeEnergyEntity, NumberEntity):
    """KEBA KeEnergy number entity."""

    entity_description: KebaKeEnergyNumberEntityDescription

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: KebaKeEnergyNumberEntityDescription,
        device_type: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        self.entity_description = description

        super().__init__(
            coordinator,
            device_type=device_type,
            index=index,
            key_index=self.entity_description.key_index,
        )

        self.entity_id: str = f"{NUMBER_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

        self._pending_key = self.entity_description.key

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        lower_limit: float | None = self.get_limit(self.entity_description.key, attr="lower_limit")
        return super().native_min_value if lower_limit is None else lower_limit * self.entity_description.scale

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        upper_limit: float | None = self.get_limit(self.entity_description.key, attr="upper_limit")
        return super().native_max_value if upper_limit is None else upper_limit * self.entity_description.scale

    @property
    def native_value(self) -> float | None:
        """Return the state of the number."""
        native_value: float | None = self._get_debounced_value()

        return None if native_value is None else self._round_float32(native_value * self.entity_description.scale)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self._schedule_debounced_write(value / self.entity_description.scale)


NUMBER_TYPES: Final[dict[str, tuple[KebaKeEnergyNumberEntityDescription, ...]]] = {
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
            condition=(
                lambda coordinator, index: (
                    coordinator.is_heating_circuit(index=index) and coordinator.has_photovoltaics()
                )
            ),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="excess_energy_heating_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="excess_energy_heating_limit_day",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=(
                lambda coordinator, index: (
                    coordinator.is_cooling_circuit(index=index) and coordinator.has_photovoltaics()
                )
            ),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="excess_energy_cooling_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="excess_energy_cooling_limit_day",
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
            condition=(
                lambda coordinator, index: (
                    coordinator.is_heating_circuit(index=index) and coordinator.has_photovoltaics()
                )
            ),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="excess_energy_heating_limit_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="excess_energy_heating_limit_night",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=(
                lambda coordinator, index: (
                    coordinator.is_cooling_circuit(index=index) and coordinator.has_photovoltaics()
                )
            ),
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="excess_energy_cooling_limit_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="excess_energy_cooling_limit_night",
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
            condition=(
                lambda coordinator, index: (
                    coordinator.is_heating_circuit(index=index) and coordinator.has_photovoltaics()
                )
            ),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="excess_energy_target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="excess_energy_target_room_temperature",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=(
                lambda coordinator, index: (
                    coordinator.is_heating_circuit(index=index) and coordinator.has_photovoltaics()
                )
            ),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="excess_energy_target_temperature_hysteresis",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.1,
            translation_key="excess_energy_target_room_temperature_hysteresis",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=(
                lambda coordinator, index: (
                    coordinator.is_cooling_circuit(index=index) and coordinator.has_photovoltaics()
                )
            ),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="excess_energy_target_cooling_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="excess_energy_target_room_cooling_temperature",
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=(
                lambda coordinator, index: (
                    coordinator.is_cooling_circuit(index=index) and coordinator.has_photovoltaics()
                )
            ),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="excess_energy_target_cooling_temperature_hysteresis",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.1,
            translation_key="excess_energy_target_room_cooling_temperature_hysteresis",
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
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="cooling_curve_slope",
            native_step=0.01,
            translation_key="cooling_curve_slope",
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
            scale=1,
        ),
        KebaKeEnergyNumberEntityDescription(
            entity_category=EntityCategory.CONFIG,
            device_class=NumberDeviceClass.TEMPERATURE,
            key="standby_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_step=0.5,
            translation_key="standby_temperature",
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
            scale=1,
        ),
    ),
    SectionPrefix.EXTERNAL_HEAT_SOURCE: (
        KebaKeEnergyNumberEntityDescription(
            entity_category=EntityCategory.CONFIG,
            device_class=NumberDeviceClass.DURATION,
            key="min_runtime_excess_energy",
            native_unit_of_measurement=UnitOfTime.MINUTES,
            native_step=1,
            translation_key="min_runtime_excess_energy",
            scale=1 / 60,
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy numbers from a config entry."""
    async_setup_entities(
        entry,
        async_add_entities,
        NUMBER_TYPES,
        KebaKeEnergyNumberEntity,
        "number",
    )
