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

from .const import BUFFER_TANK_OPERATING_MODE_TO_HA
from .const import DHW_TANK_OPERATING_MODE_TO_HA
from .const import SectionPrefix
from .entity import KebaKeEnergyBaseEntity
from .entity import KebaKeEnergyDebouncedEntity

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator

PARALLEL_UPDATES: Final[int] = 0


class KebaKeEnergyWaterHeaterEntity[M: BufferTankOperatingMode | DHWTankOperatingMode](
    KebaKeEnergyBaseEntity,
    WaterHeaterEntity,
):
    """KEBA KeEnergy water heater entity of a tank."""

    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS
    _attr_name = None
    _platform_domain: str = WATER_HEATER_DOMAIN

    # The operating modes of the tank and their operation modes in Home Assistant.
    _operating_mode_type: type[M]
    _operating_mode_to_ha: Mapping[M, str]
    # Operation modes whose writes are not counted for the weekly write limit.
    _uncounted_operation_modes: frozenset[str] = frozenset()

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: WaterHeaterEntityDescription,
        /,
        *,
        device_type: SectionPrefix,
        index: int | None,
    ) -> None:
        """Initialize the water heater entity of the tank with the index (None if it is the only one)."""
        self.entity_description: WaterHeaterEntityDescription = description
        super().__init__(coordinator, device_type=device_type, index=index)
        self._attr_operation_list: list[str] = list(self._operating_mode_to_ha.values())

    @property
    def target_temperature_low(self) -> float | None:
        """Return the standby temperature, the lower bound of the target temperature."""
        return self.get_float("standby_temperature")

    @property
    def target_temperature_high(self) -> float | None:
        """Return the target temperature, the upper bound of the target temperature."""
        return self.get_float("target_temperature")

    @property
    def current_operation(self) -> str | None:
        """Return the operation mode of the operating mode, None if it is unknown."""
        operating_mode: M | None = self.get_typed_value("operating_mode", self._operating_mode_type)
        return None if operating_mode is None else self._operating_mode_to_ha.get(operating_mode, STATE_OFF)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the tank off."""
        if self.current_operation != STATE_OFF:
            await self._async_write_value(self._operating_mode_type.OFF, key="operating_mode")

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the tank on."""
        if self.current_operation != STATE_HEAT_PUMP:
            await self._async_write_value(self._operating_mode_type.ON, key="operating_mode")

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set the operation mode of the tank."""
        for operating_mode, state in self._operating_mode_to_ha.items():
            if state == operation_mode and operation_mode != self.current_operation:
                await self._async_write_value(
                    operating_mode,
                    key="operating_mode",
                    ignore_weekly_write_count=operation_mode in self._uncounted_operation_modes,
                )


class KebaKeEnergyDHWTankEntity(
    KebaKeEnergyDebouncedEntity,
    KebaKeEnergyWaterHeaterEntity[DHWTankOperatingMode],
):
    """KEBA KeEnergy water heater entity of a DHW tank."""

    _attr_supported_features: WaterHeaterEntityFeature = (
        WaterHeaterEntityFeature.ON_OFF
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.TARGET_TEMPERATURE
    )
    _operating_mode_type: type[DHWTankOperatingMode] = DHWTankOperatingMode
    _operating_mode_to_ha: Mapping[DHWTankOperatingMode, str] = DHW_TANK_OPERATING_MODE_TO_HA
    _uncounted_operation_modes: frozenset[str] = frozenset({STATE_PERFORMANCE})

    @property
    def _debounced_key(self) -> str:
        return "target_temperature"

    @property
    def current_temperature(self) -> float | None:
        """Return the temperature at the top of the tank."""
        return self.get_float("current_temperature")

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature, a value that waits for its debounced write before the current value."""
        return self._get_debounced_value()

    @property
    def min_temp(self) -> float:
        """Return the minimum target temperature, from the lower limit of the target temperature."""
        lower_limit: float | None = self.get_limit("target_temperature", attr="lower_limit")
        return super().min_temp if lower_limit is None else lower_limit

    @property
    def max_temp(self) -> float:
        """Return the maximum target temperature, from the upper limit of the target temperature."""
        upper_limit: float | None = self.get_limit("target_temperature", attr="upper_limit")
        return super().max_temp if upper_limit is None else upper_limit

    async def async_set_temperature(self, **kwargs: object) -> None:
        """Set the target temperature of the DHW tank, written debounced."""
        temperature: object = kwargs.get(ATTR_TEMPERATURE)
        self._schedule_debounced_write(float(temperature) if isinstance(temperature, float | int) else None)


class KebaKeEnergyBufferTankEntity(KebaKeEnergyWaterHeaterEntity[BufferTankOperatingMode]):
    """KEBA KeEnergy water heater entity of a buffer tank."""

    _attr_supported_features: WaterHeaterEntityFeature = (
        WaterHeaterEntityFeature.ON_OFF | WaterHeaterEntityFeature.OPERATION_MODE
    )
    _operating_mode_type: type[BufferTankOperatingMode] = BufferTankOperatingMode
    _operating_mode_to_ha: Mapping[BufferTankOperatingMode, str] = BUFFER_TANK_OPERATING_MODE_TO_HA

    @property
    def _unique_id_parts(self) -> tuple[str, ...]:
        """Return the device type, the buffer tank has it in its unique ID unlike the DHW tank."""
        return (self.device_type,)

    @property
    def current_temperature(self) -> float | None:
        """Return the higher one of the top and bottom temperatures."""
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
        """Return the target temperature."""
        return self.get_float("target_temperature")


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy water heaters from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data
    water_heaters: list[KebaKeEnergyBufferTankEntity | KebaKeEnergyDHWTankEntity] = []
    dhw_tank_count: int = coordinator.device_count(SectionPrefix.DHW_TANK)
    buffer_tank_count: int = coordinator.device_count(SectionPrefix.BUFFER_TANK)

    water_heaters += [
        KebaKeEnergyDHWTankEntity(
            coordinator,
            WaterHeaterEntityDescription(
                key="dhw_tank",
                translation_key="dhw_tank",
            ),
            device_type=SectionPrefix.DHW_TANK,
            index=index if dhw_tank_count > 1 else None,
        )
        for index in range(dhw_tank_count)
    ]

    water_heaters += [
        KebaKeEnergyBufferTankEntity(
            coordinator,
            WaterHeaterEntityDescription(
                key="buffer_tank",
                translation_key="buffer_tank",
            ),
            device_type=SectionPrefix.BUFFER_TANK,
            index=index if buffer_tank_count > 1 else None,
        )
        for index in range(buffer_tank_count)
    ]

    async_add_entities(water_heaters)
