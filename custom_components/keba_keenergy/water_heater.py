"""Support for the KEBA KeEnergy water heater."""

from functools import cached_property
from typing import Any
from typing import Final

from homeassistant.components.water_heater import STATE_ECO
from homeassistant.components.water_heater import STATE_HEAT_PUMP
from homeassistant.components.water_heater import STATE_PERFORMANCE
from homeassistant.components.water_heater import WaterHeaterEntity
from homeassistant.components.water_heater import WaterHeaterEntityDescription
from homeassistant.components.water_heater import WaterHeaterEntityFeature
from homeassistant.components.water_heater.const import (
    DOMAIN as WATER_HEATER_DOMAIN,
)
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import STATE_OFF
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HassJob
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from keba_keenergy_api.constants import BufferTank
from keba_keenergy_api.constants import BufferTankOperatingMode
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import HotWaterTankOperatingMode
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .const import FLASH_WRITE_DELAY
from .coordinator import KebaKeEnergyConfigEntry
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyEntity

PARALLEL_UPDATES: Final[int] = 0

HOT_WATER_TANK_STATE_TO_HA: Final[dict[int, str]] = {
    HotWaterTankOperatingMode.AUTO.value: STATE_ECO,
    HotWaterTankOperatingMode.HEAT_UP.value: STATE_PERFORMANCE,
    HotWaterTankOperatingMode.OFF.value: STATE_OFF,
    HotWaterTankOperatingMode.ON.value: STATE_HEAT_PUMP,
}

BUFFER_TANK_STATE_TO_HA: Final[dict[int, str]] = {
    BufferTankOperatingMode.HEAT_UP.value: STATE_PERFORMANCE,
    BufferTankOperatingMode.OFF.value: STATE_OFF,
    BufferTankOperatingMode.ON.value: STATE_HEAT_PUMP,
}


class KebaKeEnergyWaterHeaterTankEntity(KebaKeEnergyEntity, WaterHeaterEntity):
    """KEBA KeEnergy water heat entity."""

    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS
    _attr_name = None

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: WaterHeaterEntityDescription,
        entry: KebaKeEnergyConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: WaterHeaterEntityDescription = description
        super().__init__(coordinator, entry=entry, section_id=section_id, index=index)

    @property
    def target_temperature_low(self) -> float | None:
        """Return the low bound target temperature we try to reach."""
        return self.get_value("standby_temperature", expected_type=float)

    @property
    def target_temperature_high(self) -> float | None:
        """Return the high bound target temperature we try to reach."""
        return self.get_value("target_temperature", expected_type=float)


class KebaKeEnergyHotWaterTankEntity(KebaKeEnergyWaterHeaterTankEntity, WaterHeaterEntity):
    """KEBA KeEnergy water heat entity for hot water tank."""

    _attr_supported_features: WaterHeaterEntityFeature = (
        WaterHeaterEntityFeature.ON_OFF
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.TARGET_TEMPERATURE
    )

    _attr_operation_list: list[str] = list(HOT_WATER_TANK_STATE_TO_HA.values())  # noqa: RUF012

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: WaterHeaterEntityDescription,
        entry: KebaKeEnergyConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, description=description, entry=entry, section_id=section_id, index=index)

        self.entity_id: str = f"{WATER_HEATER_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

        self._pending_key = "target_temperature_offset"
        self._pending_section = HotWaterTank.TARGET_TEMPERATURE
        self._pending_device_numbers = self.coordinator.hot_water_tank_numbers

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.get_value("current_temperature", expected_type=float)

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        target_temperature: float | None

        if self._pending_value is not None and self._async_call_later:
            target_temperature = self._pending_value
        else:
            target_temperature = self.get_value("target_temperature", expected_type=float)

        return target_temperature

    @cached_property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return float(self.get_attribute("target_temperature", attr="lower_limit"))

    @cached_property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return float(self.get_attribute("target_temperature", attr="upper_limit"))

    @property
    def current_operation(self) -> str | None:
        """Return current operation mode."""
        _current_operation: str = STATE_OFF
        operating_mode: str | None = self.get_value("operating_mode", expected_type=str)

        for key, value in HOT_WATER_TANK_STATE_TO_HA.items():
            if HotWaterTankOperatingMode(key).name.lower() == operating_mode:
                _current_operation = value
                break

        return _current_operation

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the hot water tank off."""
        if self.current_operation != STATE_OFF:
            await self._async_write_data(
                HotWaterTankOperatingMode.OFF.value,
                section=HotWaterTank.OPERATING_MODE,
                device_numbers=self.coordinator.hot_water_tank_numbers,
            )

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the hot water tank on."""
        if self.current_operation != STATE_HEAT_PUMP:
            await self._async_write_data(
                HotWaterTankOperatingMode.ON.value,
                section=HotWaterTank.OPERATING_MODE,
                device_numbers=self.coordinator.hot_water_tank_numbers,
            )

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set operation mode for hot water tank."""
        for key, value in HOT_WATER_TANK_STATE_TO_HA.items():
            if value == operation_mode and operation_mode != self.current_operation:
                await self._async_write_data(
                    key,
                    section=HotWaterTank.OPERATING_MODE,
                    device_numbers=self.coordinator.hot_water_tank_numbers,
                    ignore_daily_write_count=operation_mode == STATE_PERFORMANCE,
                )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set temperature for hot water tank."""
        if temperature := kwargs.get(ATTR_TEMPERATURE):
            self._pending_value = temperature

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


class KebaKeEnergyBufferTankEntity(KebaKeEnergyWaterHeaterTankEntity, WaterHeaterEntity):
    """KEBA KeEnergy water heat entity for buffer tank."""

    _attr_supported_features: WaterHeaterEntityFeature = (
        WaterHeaterEntityFeature.ON_OFF | WaterHeaterEntityFeature.OPERATION_MODE
    )

    _attr_operation_list: list[str] = list(BUFFER_TANK_STATE_TO_HA.values())  # noqa: RUF012

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: WaterHeaterEntityDescription,
        entry: KebaKeEnergyConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, description=description, entry=entry, section_id=section_id, index=index)

        self._attr_unique_id: str | None = f"{self.entry.unique_id}_{self.section_id}"

        if self.position is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.position}"

        self.entity_id: str = f"{WATER_HEATER_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        values: list[float] = [
            value
            for value in (
                self.get_value("current_top_temperature", expected_type=float),
                self.get_value("current_bottom_temperature", expected_type=float),
            )
            if value is not None
        ]

        return max(values) if values else None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.get_value("target_temperature", expected_type=float)

    @property
    def current_operation(self) -> str | None:
        """Return current operation mode."""
        _current_operation: str | None = None
        operating_mode: str | None = self.get_value("operating_mode", expected_type=str)

        if operating_mode:
            _current_operation = STATE_OFF

            for key, value in BUFFER_TANK_STATE_TO_HA.items():
                if BufferTankOperatingMode(key).name.lower() == operating_mode:
                    _current_operation = value
                    break

        return _current_operation

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the buffer tank off."""
        if self.current_operation != STATE_OFF:
            await self._async_write_data(
                BufferTankOperatingMode.OFF.value,
                section=BufferTank.OPERATING_MODE,
                device_numbers=self.coordinator.buffer_tank_numbers,
            )

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the buffer tank on."""
        if self.current_operation != STATE_HEAT_PUMP:
            await self._async_write_data(
                BufferTankOperatingMode.ON.value,
                section=BufferTank.OPERATING_MODE,
                device_numbers=self.coordinator.buffer_tank_numbers,
            )

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set operation mode for buffer tank."""
        for key, value in BUFFER_TANK_STATE_TO_HA.items():
            if value == operation_mode and operation_mode != self.current_operation:
                await self._async_write_data(
                    key,
                    section=BufferTank.OPERATING_MODE,
                    device_numbers=self.coordinator.buffer_tank_numbers,
                )


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy water heaters from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data
    water_heaters: list[KebaKeEnergyWaterHeaterTankEntity] = []

    water_heaters += [
        KebaKeEnergyHotWaterTankEntity(
            coordinator,
            description=WaterHeaterEntityDescription(
                key="hot_water_tank",
                translation_key="hot_water_tank",
            ),
            entry=entry,
            section_id=SectionPrefix.HOT_WATER_TANK.value,
            index=index if coordinator.hot_water_tank_numbers > 1 else None,
        )
        for index in range(coordinator.hot_water_tank_numbers)
    ]

    water_heaters += [
        KebaKeEnergyBufferTankEntity(
            coordinator,
            description=WaterHeaterEntityDescription(
                key="buffer_tank",
                translation_key="buffer_tank",
            ),
            entry=entry,
            section_id=SectionPrefix.BUFFER_TANK.value,
            index=index if coordinator.buffer_tank_numbers > 1 else None,
        )
        for index in range(coordinator.buffer_tank_numbers)
    ]

    async_add_entities(water_heaters)
