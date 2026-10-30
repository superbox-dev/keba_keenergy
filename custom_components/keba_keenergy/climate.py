# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Support for the KEBA KeEnergy climate."""

from __future__ import annotations

import logging
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Final

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate import ClimateEntityDescription
from homeassistant.components.climate.const import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.climate.const import PRESET_AWAY
from homeassistant.components.climate.const import PRESET_HOME
from homeassistant.components.climate.const import ClimateEntityFeature
from homeassistant.components.climate.const import HVACAction
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import UnitOfTemperature
from homeassistant.util import dt as dt_util
from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import HeatingCircuitRequest

from .const import COOLING_CIRCUIT_PRESET_TO_HA
from .const import DOMAIN
from .const import HEAT_PUMP_STATE_TO_HVAC_ACTION
from .const import HEATING_CIRCUIT_PRESET_TO_HA
from .const import SectionPrefix
from .entity import KebaKeEnergyDebouncedEntity

if TYPE_CHECKING:
    from collections.abc import Mapping
    from zoneinfo import ZoneInfo

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from keba_keenergy_api.enums import HeatPumpState

    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator

_LOGGER: Final = logging.getLogger(__name__)

PARALLEL_UPDATES: Final[int] = 0


class KebaKeEnergyClimateEntity(KebaKeEnergyDebouncedEntity, ClimateEntity):
    """KEBA KeEnergy climate entity."""

    _attr_supported_features: ClimateEntityFeature = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )

    _attr_target_temperature_step: float = 0.5
    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS
    _attr_name = None

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: ClimateEntityDescription,
        device_type: SectionPrefix,
        index: int | None,
    ) -> None:
        """Initialize KEBA KeEnergy climate entity."""
        self.entity_description = description

        super().__init__(coordinator, device_type=device_type, index=index)

        self.entity_id = f"{CLIMATE_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def _debounced_key(self) -> str:
        return "target_temperature_offset"

    @cached_property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available hvac operation modes."""
        return [HVACMode.AUTO, self._hvac_mode_on, HVACMode.OFF]

    @cached_property
    def _hvac_mode_on(self) -> HVACMode:
        # A heating circuit that supports heating and cooling uses HEAT_COOL, this is untested with a real device.
        return HVACMode.HEAT if self._is_heating else HVACMode.COOL if self._is_cooling else HVACMode.HEAT_COOL

    @cached_property
    def _is_heating(self) -> bool:
        return self.coordinator.is_heating_circuit(index=self.index) and not self.coordinator.is_cooling_circuit(
            index=self.index,
        )

    @cached_property
    def _is_cooling(self) -> bool:
        return self.coordinator.is_cooling_circuit(index=self.index) and not self.coordinator.is_heating_circuit(
            index=self.index,
        )

    @cached_property
    def preset_modes(self) -> list[str] | None:
        """Return available preset modes."""
        preset_to_ha: Mapping[HeatingCircuitOperatingMode, str] = HEATING_CIRCUIT_PRESET_TO_HA

        if self._is_cooling:
            preset_to_ha = COOLING_CIRCUIT_PRESET_TO_HA

        return list(preset_to_ha.values())

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.get_float("room_temperature")

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        selected_target_temperature: float | None = self.get_float("selected_target_temperature")
        target_temperature_offset: float | None = self._get_debounced_value()

        return (
            None
            if selected_target_temperature is None or target_temperature_offset is None
            else selected_target_temperature + target_temperature_offset
        )

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        selected_target_temperature: float | None = self.get_float("selected_target_temperature")
        lower_limit: float | None = self.get_limit("target_temperature_offset", attr="lower_limit")

        return (
            super().min_temp
            if selected_target_temperature is None or lower_limit is None
            else selected_target_temperature + lower_limit
        )

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        selected_target_temperature: float | None = self.get_float("selected_target_temperature")
        upper_limit: float | None = self.get_limit("target_temperature_offset", attr="upper_limit")

        return (
            super().max_temp
            if selected_target_temperature is None or upper_limit is None
            else selected_target_temperature + upper_limit
        )

    @property
    def current_humidity(self) -> float | None:
        """Return the current humidity."""
        return self.get_float("room_humidity")

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation."""
        operating_mode: HeatingCircuitOperatingMode | None = self._operating_mode
        return None if operating_mode is None else self._operating_mode_to_hvac_mode(operating_mode)

    @property
    def _operating_mode(self) -> HeatingCircuitOperatingMode | None:
        return self.get_typed_value("operating_mode", HeatingCircuitOperatingMode)

    def _operating_mode_to_hvac_mode(self, operating_mode: HeatingCircuitOperatingMode, /) -> HVACMode:
        if operating_mode is HeatingCircuitOperatingMode.AUTO:
            return HVACMode.AUTO

        if operating_mode in HEATING_CIRCUIT_PRESET_TO_HA:
            return self._hvac_mode_on

        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation if supported."""
        has_heat_request: bool = self.get_value("heat_request") is HeatingCircuitRequest.ACTIVE
        has_cool_request: bool = self.get_value("cool_request") is HeatingCircuitRequest.ACTIVE

        # Cooling only uses the cool request, the heat pump stays in standby with passive cooling.
        return (
            HVACAction.OFF
            if self.hvac_mode == HVACMode.OFF
            else self._heating_action
            if has_heat_request
            else HVACAction.COOLING
            if has_cool_request
            else HVACAction.IDLE
        )

    @property
    def _heating_action(self) -> HVACAction:
        # The heat request of the heating circuit is only its demand, the heat pump state shows if it is heated.
        # Newer software versions keep the heat request on during the whole heating period, also in standby.
        # The API has no mapping of the heating circuits to the heat pumps, so the state of any heat pump counts.
        # A heating circuit that is supplied by a buffer tank while the heat pumps are in standby is idle.
        heat_pump_states: set[HeatPumpState] = self.coordinator.heat_pump_states

        return next(
            (
                hvac_action
                for heat_pump_state, hvac_action in HEAT_PUMP_STATE_TO_HVAC_ACTION.items()
                if heat_pump_state in heat_pump_states
            ),
            HVACAction.IDLE,
        )

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        operating_mode: HeatingCircuitOperatingMode | None = self._operating_mode

        # Off and the modes without a preset (e.g. external or room control) return the home preset.
        return PRESET_HOME if operating_mode is None else HEATING_CIRCUIT_PRESET_TO_HA.get(operating_mode, PRESET_HOME)

    async def async_turn_off(self) -> None:
        """Turn off the heat circuit."""
        await self.async_set_hvac_mode(hvac_mode=HVACMode.OFF)

    async def async_turn_on(self) -> None:
        """Turn on the heat circuit."""
        await self.async_set_hvac_mode(hvac_mode=HVACMode.AUTO)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set hvac mode for heat circuit."""
        operating_mode_status: HeatingCircuitOperatingMode = (
            HeatingCircuitOperatingMode.AUTO
            if hvac_mode == HVACMode.AUTO
            else HeatingCircuitOperatingMode.OFF
            if hvac_mode == HVACMode.OFF
            else HeatingCircuitOperatingMode.NORMAL
        )

        if hvac_mode == HVACMode.AUTO:
            await self._async_set_away_date_range(PRESET_HOME)

        if self._operating_mode is not operating_mode_status:
            await self._async_write_data(
                operating_mode_status,
                key="operating_mode",
            )

    async def _async_set_away_date_range(self, preset_mode: str, /) -> None:
        is_away: bool = preset_mode == PRESET_AWAY

        # The time zone is only requested if the away date range changes.
        if not is_away and self.preset_mode != PRESET_AWAY:
            return

        tz: ZoneInfo = await self.coordinator.async_get_timezone()
        now: date = dt_util.now(tz).date()
        start_date_tz: datetime = datetime.combine(now, time.min, tzinfo=tz)
        end_date_tz: datetime = datetime.combine(now, time.max, tzinfo=tz)

        if is_away:
            await self.coordinator.async_set_away_date_range(
                start_timestamp=start_date_tz.timestamp(),
                end_timestamp=(end_date_tz + timedelta(days=365)).timestamp(),
            )
        else:
            await self.coordinator.async_set_away_date_range(
                start_timestamp=(start_date_tz - timedelta(days=1)).timestamp(),
                end_timestamp=(end_date_tz - timedelta(days=1)).timestamp(),
            )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode for heat circuit."""
        await self._async_set_away_date_range(preset_mode)

        for operating_mode, preset in HEATING_CIRCUIT_PRESET_TO_HA.items():
            if preset == preset_mode and preset_mode not in (self.preset_mode, PRESET_AWAY):
                await self._async_write_data(
                    operating_mode,
                    key="operating_mode",
                )

    async def async_set_temperature(self, **kwargs: object) -> None:
        """Set new target temperature."""
        temperature: object = kwargs.get(ATTR_TEMPERATURE)
        selected_target_temperature: float | None = self.get_float("selected_target_temperature")

        self._schedule_debounced_write(
            temperature - selected_target_temperature
            if isinstance(temperature, float | int) and selected_target_temperature is not None
            else None,
        )


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy climates from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data
    heat_circuit_numbers: int = coordinator.device_count(SectionPrefix.HEAT_CIRCUIT)
    climates: list[KebaKeEnergyClimateEntity] = [
        KebaKeEnergyClimateEntity(
            coordinator,
            description=ClimateEntityDescription(
                key="heat_circuit",
                translation_key="heat_circuit",
            ),
            device_type=SectionPrefix.HEAT_CIRCUIT,
            index=index if heat_circuit_numbers > 1 else None,
        )
        for index in range(heat_circuit_numbers)
    ]

    async_add_entities(climates)
