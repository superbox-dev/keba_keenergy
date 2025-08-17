"""Support for the KEBA KeEnergy climate."""
from typing import Any, Final
import logging

from keba_keenergy_api.constants import (
    HeatCircuit,
    HeatCircuitHeatRequest,
    HeatCircuitOperatingMode,
    SectionPrefix,
)
import voluptuous as vol

from homeassistant.components.climate import (
    DOMAIN as CLIMATE_DOMAIN,
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_NONE,
    PRESET_SLEEP,
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KebaKeEnergyDataUpdateCoordinator
from .const import ATTR_OFFSET, DOMAIN
from .entity import KebaKeEnergyEntity

HEAT_CIRCUIT_PRESET_TO_HA: Final[dict[int, str]] = {
    HeatCircuitOperatingMode.AUTO: PRESET_NONE,
    HeatCircuitOperatingMode.HOLIDAY: PRESET_AWAY,
    HeatCircuitOperatingMode.DAY: PRESET_COMFORT,
    HeatCircuitOperatingMode.NIGHT: PRESET_SLEEP,
    HeatCircuitOperatingMode.PARTY: PRESET_BOOST,
}

HEAT_CIRCUIT_HVAC_ACTION_TO_HA: Final[dict[str, HVACAction]] = {
    HeatCircuitHeatRequest.OFF: HVACAction.IDLE,
    HeatCircuitHeatRequest.ON: HVACAction.HEATING,
    HeatCircuitHeatRequest.TEMPORARY_OFF: HVACAction.IDLE,
    HeatCircuitHeatRequest.OUTDOOR_TEMPERATURE_OFF: HVACAction.IDLE,
}

TEMPERATURE_OFFSET_SCHEMA = {
    vol.Required(ATTR_OFFSET, default=0): vol.Coerce(float),
}

TEMPERATURE_SCHEMA = {
    vol.Required(ATTR_TEMPERATURE): vol.Coerce(float),
}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up KEBA KeEnergy climates from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    climates: list[KebaKeEnergyClimateEntity] = []

    for index in range(coordinator.heat_circuit_numbers):
        climates.append(
            KebaKeEnergyClimateEntity(
                coordinator=coordinator,
                description=ClimateEntityDescription(
                    key="heat_circuit",
                    translation_key="heat_circuit",
                ),
                entry=entry,
                section_id=SectionPrefix.HEAT_CIRCUIT.value,
                index=index if coordinator.heat_circuit_numbers > 1 else None,
            )
        )

    async_add_entities(climates)


class KebaKeEnergyClimateEntity(KebaKeEnergyEntity, ClimateEntity):
    """KEBA KeEnergy climate entity."""

    _attr_supported_features: ClimateEntityFeature = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )

    _attr_hvac_modes: list[HVACMode] = [
        HVACMode.AUTO,
        HVACMode.HEAT,
        HVACMode.OFF,
    ]
    _attr_preset_modes: list[str] = list(HEAT_CIRCUIT_PRESET_TO_HA.values())

    _attr_target_temperature_step: float = 0.5
    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS
    _attr_name = None

    _enable_turn_on_off_backwards_compatibility = False

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: ClimateEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize KEBA KeEnergy climate entity."""
        super().__init__(coordinator, entry, section_id, index)
        self.entity_description = description

        self._attr_unique_id = entry.unique_id
        if self.position is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.position}"

        self.entity_id = f"{CLIMATE_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        return "mdi:hvac" if self.hvac_mode == HVACMode.HEAT else "mdi:hvac-off"

    @property
    def target_temperature_for_preset(self) -> float:
        """Return the temperature for the current preset."""
        target_temperature = float(self.get_value("day_temperature"))

        if self.preset_mode == PRESET_SLEEP:
            target_temperature = float(self.get_value("night_temperature"))
        elif self.preset_mode == PRESET_AWAY:
            target_temperature = float(self.get_value("holiday_temperature"))

        return target_temperature

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.target_temperature_for_preset + float(
            self.get_value("temperature_offset")
        )

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self.target_temperature_for_preset + float(
            self.get_attribute("temperature_offset", "lower_limit")
        )

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self.target_temperature_for_preset + float(
            self.get_attribute("temperature_offset", "upper_limit")
        )

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation."""
        operating_mode: str = self.get_value("operating_mode")

        if (
            HeatCircuitOperatingMode[operating_mode.upper()].value
            == HeatCircuitOperatingMode.AUTO
        ):
            return HVACMode.AUTO

        if HeatCircuitOperatingMode[operating_mode.upper()].value in [
            HeatCircuitOperatingMode.HOLIDAY,
            HeatCircuitOperatingMode.DAY,
            HeatCircuitOperatingMode.NIGHT,
            HeatCircuitOperatingMode.PARTY,
        ]:
            return HVACMode.HEAT

        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation if supported."""
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF

        heat_request: str = self.get_value("heat_request")

        return HEAT_CIRCUIT_HVAC_ACTION_TO_HA[
            HeatCircuitHeatRequest[heat_request.upper()].value
        ]

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        self._attr_preset_mode = PRESET_NONE
        operating_mode: str = self.get_value("operating_mode")

        if (
            HeatCircuitOperatingMode[operating_mode.upper()].value
            != HeatCircuitOperatingMode.OFF
        ):
            self._attr_preset_mode = HEAT_CIRCUIT_PRESET_TO_HA[
                HeatCircuitOperatingMode[operating_mode.upper()].value
            ]

        _LOGGER.debug("preset_mode %s", self._attr_preset_mode)
        return self._attr_preset_mode

    async def async_turn_off(self) -> None:
        """Turn off the heat circuit."""
        await self.async_set_hvac_mode(hvac_mode=HVACMode.OFF)

    async def async_turn_on(self) -> None:
        """Turn on the heat circuit."""
        await self.async_set_hvac_mode(hvac_mode=HVACMode.AUTO)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set hvac mode for heat circuit."""
        operating_mode_status: int | None = None

        if hvac_mode == HVACMode.AUTO:
            operating_mode_status = HeatCircuitOperatingMode.AUTO
            self._attr_preset_mode = PRESET_NONE
        elif hvac_mode == HVACMode.HEAT:
            operating_mode_status = HeatCircuitOperatingMode.DAY
        elif hvac_mode == HVACMode.OFF:
            operating_mode_status = HeatCircuitOperatingMode.OFF

        if operating_mode_status is not None:
            await self._async_update_data(
                section=HeatCircuit.OPERATING_MODE,
                value=operating_mode_status,
                device_numbers=self.coordinator.heat_circuit_numbers,
            )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode for heat circuit."""
        for key, value in HEAT_CIRCUIT_PRESET_TO_HA.items():
            if value == preset_mode:
                await self._async_update_data(
                    section=HeatCircuit.OPERATING_MODE,
                    value=key,
                    device_numbers=self.coordinator.heat_circuit_numbers,
                )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if temperature := kwargs.get(ATTR_TEMPERATURE):
            await self._async_update_data(
                section=HeatCircuit.TEMPERATURE_OFFSET,
                value=temperature - self.target_temperature_for_preset,
                device_numbers=self.coordinator.heat_circuit_numbers,
            )
