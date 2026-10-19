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

import probatio
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate import ClimateEntityDescription
from homeassistant.components.climate.const import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.climate.const import PRESET_AWAY
from homeassistant.components.climate.const import PRESET_BOOST
from homeassistant.components.climate.const import PRESET_COMFORT
from homeassistant.components.climate.const import PRESET_HOME
from homeassistant.components.climate.const import PRESET_SLEEP
from homeassistant.components.climate.const import ClimateEntityFeature
from homeassistant.components.climate.const import HVACAction
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import UnitOfTemperature
from homeassistant.util import dt as dt_util
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatCircuitCoolRequest
from keba_keenergy_api.constants import HeatCircuitHeatRequest
from keba_keenergy_api.constants import HeatCircuitOperatingMode
from keba_keenergy_api.constants import SectionPrefix

from .const import ATTR_OFFSET
from .const import DOMAIN
from .entity import KebaKeEnergyBaseEntity

if TYPE_CHECKING:
    from zoneinfo import ZoneInfo

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES: Final[int] = 0

HEATING_CIRCUIT_PRESET_TO_HA: Final[dict[int, str]] = {
    HeatCircuitOperatingMode.AUTO.value: PRESET_HOME,
    HeatCircuitOperatingMode.HOLIDAY.value: PRESET_AWAY,
    HeatCircuitOperatingMode.DAY.value: PRESET_COMFORT,
    HeatCircuitOperatingMode.NIGHT.value: PRESET_SLEEP,
    HeatCircuitOperatingMode.PARTY.value: PRESET_BOOST,
}

COOLING_CIRCUIT_PRESET_TO_HA: Final[dict[int, str]] = {
    HeatCircuitOperatingMode.AUTO.value: PRESET_HOME,
    HeatCircuitOperatingMode.DAY.value: PRESET_COMFORT,
    HeatCircuitOperatingMode.NIGHT.value: PRESET_SLEEP,
    HeatCircuitOperatingMode.PARTY.value: PRESET_BOOST,
}

TEMPERATURE_OFFSET_SCHEMA = {
    probatio.Required(ATTR_OFFSET, default=0): probatio.Coerce(float),
}

TEMPERATURE_SCHEMA = {
    probatio.Required(ATTR_TEMPERATURE): probatio.Coerce(float),
}


class KebaKeEnergyClimateEntity(KebaKeEnergyBaseEntity, ClimateEntity):
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
        entry: KebaKeEnergyConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize KEBA KeEnergy climate entity."""
        self.entity_description = description

        super().__init__(coordinator, entry, section_id, index)

        self.entity_id = f"{CLIMATE_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

        self._pending_key = "target_temperature_offset"
        self._pending_section = HeatCircuit.TARGET_TEMPERATURE_OFFSET

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
    def _hvac_mode_on(self) -> HVACMode:
        # A heating circuit that supports heating and cooling uses HEAT_COOL, this is untested with a real device
        return HVACMode.HEAT if self._is_heating else HVACMode.COOL if self._is_cooling else HVACMode.HEAT_COOL

    @cached_property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available hvac operation modes."""
        return [HVACMode.AUTO, self._hvac_mode_on, HVACMode.OFF]

    @cached_property
    def preset_modes(self) -> list[str] | None:
        """Return available preset modes."""
        preset_to_ha: dict[int, str] = HEATING_CIRCUIT_PRESET_TO_HA

        if self._is_cooling:
            preset_to_ha = COOLING_CIRCUIT_PRESET_TO_HA

        return list(preset_to_ha.values())

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return (
            self.get_value("room_temperature", expected_type=float)
            if self.coordinator.has_room_temperature(index=self.index)
            else None
        )

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        selected_target_temperature: float | None = self.get_value("selected_target_temperature", expected_type=float)
        target_temperature_offset: float | None = self._get_debounced_value()

        return (
            None
            if selected_target_temperature is None or target_temperature_offset is None
            else selected_target_temperature + target_temperature_offset
        )

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        selected_target_temperature: float | None = self.get_value("selected_target_temperature", expected_type=float)
        lower_limit: float | None = self.get_limit("target_temperature_offset", attr="lower_limit")

        return (
            super().min_temp
            if selected_target_temperature is None or lower_limit is None
            else selected_target_temperature + lower_limit
        )

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        selected_target_temperature: float | None = self.get_value("selected_target_temperature", expected_type=float)
        upper_limit: float | None = self.get_limit("target_temperature_offset", attr="upper_limit")

        return (
            super().max_temp
            if selected_target_temperature is None or upper_limit is None
            else selected_target_temperature + upper_limit
        )

    @property
    def current_humidity(self) -> float | None:
        """Return the current humidity."""
        return (
            self.get_value("room_humidity", expected_type=float)
            if self.coordinator.has_room_humidity(index=self.index)
            else None
        )

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation."""
        operating_mode: str | None = self.get_value("operating_mode", expected_type=str)
        return None if operating_mode is None else self._operating_mode_to_hvac_mode(operating_mode)

    def _operating_mode_to_hvac_mode(self, operating_mode: str, /) -> HVACMode:
        mode: int = HeatCircuitOperatingMode[operating_mode.upper()].value

        if mode == HeatCircuitOperatingMode.AUTO.value:
            return HVACMode.AUTO

        if mode in HEATING_CIRCUIT_PRESET_TO_HA:
            return self._hvac_mode_on

        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation if supported."""
        has_heat_request: bool = HeatCircuitHeatRequest.ON.name.lower() == self.get_value(
            "heat_request",
            expected_type=str,
        )
        has_cool_request: bool = HeatCircuitCoolRequest.ON.name.lower() == self.get_value(
            "cool_request",
            expected_type=str,
        )

        return (
            HVACAction.OFF
            if self.hvac_mode == HVACMode.OFF
            else HVACAction.HEATING
            if has_heat_request
            else HVACAction.COOLING
            if has_cool_request
            else HVACAction.IDLE
        )

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        operating_mode: str | None = self.get_value("operating_mode", expected_type=str)

        # Off and the modes without a preset (e.g. external or room control) return the home preset
        return (
            HEATING_CIRCUIT_PRESET_TO_HA.get(HeatCircuitOperatingMode[operating_mode.upper()].value, PRESET_HOME)
            if operating_mode
            else PRESET_HOME
        )

    async def async_turn_off(self) -> None:
        """Turn off the heat circuit."""
        await self.async_set_hvac_mode(hvac_mode=HVACMode.OFF)

    async def async_turn_on(self) -> None:
        """Turn on the heat circuit."""
        await self.async_set_hvac_mode(hvac_mode=HVACMode.AUTO)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set hvac mode for heat circuit."""
        operating_mode_status: int = (
            HeatCircuitOperatingMode.AUTO.value
            if hvac_mode == HVACMode.AUTO
            else HeatCircuitOperatingMode.OFF.value
            if hvac_mode == HVACMode.OFF
            else HeatCircuitOperatingMode.DAY.value
        )

        if hvac_mode == HVACMode.AUTO:
            await self._async_set_away_date_range(PRESET_HOME)

        operating_mode: str | None = self.get_value("operating_mode", expected_type=str)

        if operating_mode is None or HeatCircuitOperatingMode[operating_mode.upper()].value != operating_mode_status:
            await self._async_write_data(
                operating_mode_status,
                section=HeatCircuit.OPERATING_MODE,
                device_numbers=self.device_numbers,
            )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode for heat circuit."""
        await self._async_set_away_date_range(preset_mode)

        for key, value in HEATING_CIRCUIT_PRESET_TO_HA.items():
            if value == preset_mode and preset_mode not in (self.preset_mode, PRESET_AWAY):
                await self._async_write_data(
                    key,
                    section=HeatCircuit.OPERATING_MODE,
                    device_numbers=self.device_numbers,
                )

    async def async_set_temperature(self, **kwargs: object) -> None:
        """Set new target temperature."""
        temperature: object = kwargs.get(ATTR_TEMPERATURE)
        selected_target_temperature: float | None = self.get_value("selected_target_temperature", expected_type=float)

        self._schedule_debounced_write(
            temperature - selected_target_temperature
            if isinstance(temperature, float | int) and selected_target_temperature is not None
            else None,
        )

    async def _async_set_away_date_range(self, preset_mode: str, /) -> None:
        is_away: bool = preset_mode == PRESET_AWAY

        # The time zone is only requested if the away date range changes
        if not is_away and self.preset_mode != PRESET_AWAY:
            return

        tz: ZoneInfo = await self.coordinator.get_timezone()
        now: date = dt_util.now(tz).date()
        start_date_tz: datetime = datetime.combine(now, time.min, tzinfo=tz)
        end_date_tz: datetime = datetime.combine(now, time.max, tzinfo=tz)

        if is_away:
            await self.coordinator.set_away_date_range(
                start_timestamp=start_date_tz.timestamp(),
                end_timestamp=(end_date_tz + timedelta(days=365)).timestamp(),
            )
        else:
            await self.coordinator.set_away_date_range(
                start_timestamp=(start_date_tz - timedelta(days=1)).timestamp(),
                end_timestamp=(end_date_tz - timedelta(days=1)).timestamp(),
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
            entry=entry,
            section_id=SectionPrefix.HEAT_CIRCUIT.value,
            index=index if heat_circuit_numbers > 1 else None,
        )
        for index in range(heat_circuit_numbers)
    ]

    async_add_entities(climates)
