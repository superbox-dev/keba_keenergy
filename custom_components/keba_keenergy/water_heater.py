"""Support for the KEBA KeEnergy water heater."""

from typing import Any
from typing import Final

from homeassistant.components.water_heater import STATE_ECO
from homeassistant.components.water_heater import STATE_HEAT_PUMP
from homeassistant.components.water_heater import STATE_PERFORMANCE
from homeassistant.components.water_heater import WaterHeaterEntity
from homeassistant.components.water_heater import WaterHeaterEntityEntityDescription
from homeassistant.components.water_heater import WaterHeaterEntityFeature
from homeassistant.components.water_heater.const import (
    DOMAIN as WATER_HEATER_DOMAIN,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import STATE_OFF
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import HotWaterTankOperatingMode
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyEntity

HOT_WATER_TANK_STATE_TO_HA: Final[dict[int, str]] = {
    HotWaterTankOperatingMode.AUTO.value: STATE_ECO,
    HotWaterTankOperatingMode.HEAT_UP.value: STATE_PERFORMANCE,
    HotWaterTankOperatingMode.OFF.value: STATE_OFF,
    HotWaterTankOperatingMode.ON.value: STATE_HEAT_PUMP,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy water heaters from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    water_heaters: list[KebaKeEnergyWaterHeaterEntity] = [
        KebaKeEnergyWaterHeaterEntity(
            coordinator=coordinator,
            description=WaterHeaterEntityEntityDescription(
                key="hot_water_tank",
                translation_key="hot_water_tank",
            ),
            entry=entry,
            section_id=SectionPrefix.HOT_WATER_TANK.value,
            index=index if coordinator.hot_water_tank_numbers > 1 else None,
        )
        for index in range(coordinator.hot_water_tank_numbers)
    ]

    async_add_entities(water_heaters)


class KebaKeEnergyWaterHeaterEntity(KebaKeEnergyEntity, WaterHeaterEntity):
    """KEBA KeEnergy water heat entity."""

    _attr_supported_features: WaterHeaterEntityFeature = (
        WaterHeaterEntityFeature.ON_OFF
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.TARGET_TEMPERATURE
    )

    _attr_operation_list: list[str] = list(HOT_WATER_TANK_STATE_TO_HA.values())  # noqa: RUF012
    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS
    _attr_name = None

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: WaterHeaterEntityEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, entry, section_id, index)
        self.entity_description = description

        self._attr_unique_id = entry.unique_id
        if self.position is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.position}"

        self.entity_id = f"{WATER_HEATER_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return float(self.get_value("temperature"))

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return float(self.get_attribute("min_temperature", "lower_limit"))

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return float(self.get_attribute("max_temperature", "upper_limit"))

    @property
    def current_operation(self) -> str:
        """Return current operation mode."""
        _current_operation: str = STATE_OFF
        operating_mode: str = self.get_value("operating_mode")

        for key, value in HOT_WATER_TANK_STATE_TO_HA.items():
            if HotWaterTankOperatingMode(key).name.lower() == operating_mode:
                _current_operation = value
                break

        return _current_operation

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return float(self.get_value("max_temperature"))

    @property
    def target_temperature_low(self) -> float:
        """Return the lowbound target temperature we try to reach."""
        return float(self.get_value("min_temperature"))

    @property
    def target_temperature_high(self) -> float | None:
        """Return the highbound target temperature we try to reach."""
        return float(self.get_attribute("max_temperature", "upper_limit"))

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the hot water tank off."""
        await self._async_update_data(
            section=HotWaterTank.OPERATING_MODE,
            value=HotWaterTankOperatingMode.OFF.value,
            device_numbers=self.coordinator.hot_water_tank_numbers,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the hot water tank on (heat up mode)."""
        await self._async_update_data(
            section=HotWaterTank.OPERATING_MODE,
            value=HotWaterTankOperatingMode.HEAT_UP.value,
            device_numbers=self.coordinator.hot_water_tank_numbers,
        )

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set operation mode for hot water tank."""
        for key, value in HOT_WATER_TANK_STATE_TO_HA.items():
            if value == operation_mode:
                await self._async_update_data(
                    section=HotWaterTank.OPERATING_MODE,
                    value=key,
                    device_numbers=self.coordinator.hot_water_tank_numbers,
                )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set temperature for hot water tank."""
        await self._async_update_data(
            section=HotWaterTank.MAX_TEMPERATURE,
            value=kwargs[ATTR_TEMPERATURE],
            device_numbers=self.coordinator.hot_water_tank_numbers,
        )
