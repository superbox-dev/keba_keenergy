# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Support for the KEBA KeEnergy water heater."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final

from homeassistant.components.water_heater import STATE_HEAT_PUMP
from homeassistant.components.water_heater import STATE_PERFORMANCE
from homeassistant.components.water_heater import WaterHeaterEntity
from homeassistant.components.water_heater import WaterHeaterEntityDescription
from homeassistant.components.water_heater import WaterHeaterEntityFeature
from homeassistant.components.water_heater.const import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import STATE_OFF
from homeassistant.const import UnitOfTemperature
from keba_keenergy_api.enums import BufferTankOperatingMode
from keba_keenergy_api.enums import DHWTankOperatingMode

from .const import BUFFER_TANK_STATE_TO_HA
from .const import DOMAIN
from .const import HOT_WATER_TANK_STATE_TO_HA
from .const import SectionPrefix
from .entity import KebaKeEnergyBaseEntity
from .entity import KebaKeEnergyDebouncedEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator

PARALLEL_UPDATES: Final[int] = 0


class KebaKeEnergyWaterHeaterTankEntity(KebaKeEnergyBaseEntity, WaterHeaterEntity):
    """KEBA KeEnergy water heat entity."""

    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS
    _attr_name = None

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: WaterHeaterEntityDescription,
        device_type: SectionPrefix,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: WaterHeaterEntityDescription = description
        super().__init__(coordinator, device_type=device_type, index=index)

    @property
    def target_temperature_low(self) -> float | None:
        """Return the low bound target temperature we try to reach."""
        return self.get_float("standby_temperature")

    @property
    def target_temperature_high(self) -> float | None:
        """Return the high bound target temperature we try to reach."""
        return self.get_float("target_temperature")


class KebaKeEnergyHotWaterTankEntity(KebaKeEnergyDebouncedEntity, KebaKeEnergyWaterHeaterTankEntity, WaterHeaterEntity):
    """KEBA KeEnergy water heat entity for hot water tank."""

    _attr_supported_features: WaterHeaterEntityFeature = (
        WaterHeaterEntityFeature.ON_OFF
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.TARGET_TEMPERATURE
    )

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: WaterHeaterEntityDescription,
        device_type: SectionPrefix,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, description=description, device_type=device_type, index=index)
        self._attr_operation_list = list(HOT_WATER_TANK_STATE_TO_HA.values())

        self.entity_id: str = f"{WATER_HEATER_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def _debounced_key(self) -> str:
        return "target_temperature"

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.get_float("current_temperature")

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._get_debounced_value()

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        lower_limit: float | None = self.get_limit("target_temperature", attr="lower_limit")
        return super().min_temp if lower_limit is None else lower_limit

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        upper_limit: float | None = self.get_limit("target_temperature", attr="upper_limit")
        return super().max_temp if upper_limit is None else upper_limit

    @property
    def current_operation(self) -> str | None:
        """Return current operation mode."""
        operating_mode: DHWTankOperatingMode | None = self.get_typed_value("operating_mode", DHWTankOperatingMode)
        return None if operating_mode is None else HOT_WATER_TANK_STATE_TO_HA.get(operating_mode, STATE_OFF)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the hot water tank off."""
        if self.current_operation != STATE_OFF:
            await self._async_write_data(
                DHWTankOperatingMode.OFF,
                key="operating_mode",
            )

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the hot water tank on."""
        if self.current_operation != STATE_HEAT_PUMP:
            await self._async_write_data(
                DHWTankOperatingMode.ON,
                key="operating_mode",
            )

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set operation mode for hot water tank."""
        for operating_mode, state in HOT_WATER_TANK_STATE_TO_HA.items():
            if state == operation_mode and operation_mode != self.current_operation:
                await self._async_write_data(
                    operating_mode,
                    key="operating_mode",
                    ignore_weekly_write_count=operation_mode == STATE_PERFORMANCE,
                )

    async def async_set_temperature(self, **kwargs: object) -> None:
        """Set temperature for hot water tank."""
        temperature: object = kwargs.get(ATTR_TEMPERATURE)
        self._schedule_debounced_write(float(temperature) if isinstance(temperature, float | int) else None)


class KebaKeEnergyBufferTankEntity(KebaKeEnergyWaterHeaterTankEntity, WaterHeaterEntity):
    """KEBA KeEnergy water heat entity for buffer tank."""

    _attr_supported_features: WaterHeaterEntityFeature = (
        WaterHeaterEntityFeature.ON_OFF | WaterHeaterEntityFeature.OPERATION_MODE
    )

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: WaterHeaterEntityDescription,
        device_type: SectionPrefix,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, description=description, device_type=device_type, index=index)
        self._attr_operation_list = list(BUFFER_TANK_STATE_TO_HA.values())

        self._attr_unique_id: str | None = self._build_unique_id(self.device_type)

        self.entity_id: str = f"{WATER_HEATER_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        values: list[float] = [
            value
            for value in (
                self.get_float("current_top_temperature"),
                self.get_float("current_bottom_temperature"),
            )
            if value is not None
        ]

        return max(values) if values else None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.get_float("target_temperature")

    @property
    def current_operation(self) -> str | None:
        """Return current operation mode."""
        operating_mode: BufferTankOperatingMode | None = self.get_typed_value("operating_mode", BufferTankOperatingMode)
        return None if operating_mode is None else BUFFER_TANK_STATE_TO_HA.get(operating_mode, STATE_OFF)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the buffer tank off."""
        if self.current_operation != STATE_OFF:
            await self._async_write_data(
                BufferTankOperatingMode.OFF,
                key="operating_mode",
            )

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the buffer tank on."""
        if self.current_operation != STATE_HEAT_PUMP:
            await self._async_write_data(
                BufferTankOperatingMode.ON,
                key="operating_mode",
            )

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set operation mode for buffer tank."""
        for operating_mode, state in BUFFER_TANK_STATE_TO_HA.items():
            if state == operation_mode and operation_mode != self.current_operation:
                await self._async_write_data(
                    operating_mode,
                    key="operating_mode",
                )


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy water heaters from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data
    water_heaters: list[KebaKeEnergyWaterHeaterTankEntity] = []
    hot_water_tank_numbers: int = coordinator.device_count(SectionPrefix.HOT_WATER_TANK)
    buffer_tank_numbers: int = coordinator.device_count(SectionPrefix.BUFFER_TANK)

    water_heaters += [
        KebaKeEnergyHotWaterTankEntity(
            coordinator,
            description=WaterHeaterEntityDescription(
                key="hot_water_tank",
                translation_key="hot_water_tank",
            ),
            device_type=SectionPrefix.HOT_WATER_TANK,
            index=index if hot_water_tank_numbers > 1 else None,
        )
        for index in range(hot_water_tank_numbers)
    ]

    water_heaters += [
        KebaKeEnergyBufferTankEntity(
            coordinator,
            description=WaterHeaterEntityDescription(
                key="buffer_tank",
                translation_key="buffer_tank",
            ),
            device_type=SectionPrefix.BUFFER_TANK,
            index=index if buffer_tank_numbers > 1 else None,
        )
        for index in range(buffer_tank_numbers)
    ]

    async_add_entities(water_heaters)
