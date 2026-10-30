# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the KEBA KeEnergy integration."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.components.climate.const import SERVICE_SET_TEMPERATURE
from homeassistant.components.number import ATTR_VALUE
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number.const import SERVICE_SET_VALUE
from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import State
from homeassistant.core import split_entity_id
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.translation import async_get_translations
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import FLASH_WRITE_DELAY

if TYPE_CHECKING:
    from homeassistant.const import Platform
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry


async def init_translations(hass: HomeAssistant, /, *, category: str) -> dict[str, str]:
    """Return the translations of the integration for the given category."""
    translations: dict[str, str] = await async_get_translations(
        hass,
        hass.config.language,
        category,
        [DOMAIN],
    )

    return translations


def get_platform_states(hass: HomeAssistant, config_entry: MockConfigEntry, platform: Platform, /) -> list[State]:
    """Return the states of all entities of the platform of the config entry, sorted by entity ID."""
    entries: list[er.RegistryEntry] = er.async_entries_for_config_entry(er.async_get(hass), config_entry.entry_id)
    states: list[State | None] = [
        hass.states.get(entry.entity_id)
        for entry in sorted(entries, key=lambda entry: entry.entity_id)
        if entry.domain == platform
    ]
    platform_states: list[State] = [state for state in states if isinstance(state, State)]

    assert len(platform_states) == len(states), "every entity of the platform has a state"
    return platform_states


def get_state(hass: HomeAssistant, entity_id: str, /) -> State:
    """Return the state of an entity, which must exist."""
    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)
    return state


async def get_option_translations(hass: HomeAssistant, state: State, /) -> dict[str, str]:
    """Return the translated options of an entity with options (an enum sensor or a select)."""
    entry: er.RegistryEntry | None = er.async_get(hass).async_get(state.entity_id)
    assert entry is not None
    translations: dict[str, str] = await init_translations(hass, category="entity")

    return {
        option: translations[f"component.keba_keenergy.entity.{entry.domain}.{entry.translation_key}.state.{option}"]
        for option in state.attributes[ATTR_OPTIONS]
    }


async def select_option(hass: HomeAssistant, entity_id: str | list[str], option: str, /) -> None:
    """Select the option of one or more select entities with the action."""
    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_OPTION: option,
        },
        blocking=True,
    )


async def set_number_value(hass: HomeAssistant, entity_id: str, value: float | str | None, /) -> None:
    """Set the value of a number entity with the action, not written before `fire_debounced_writes()`."""
    await hass.services.async_call(
        domain=NUMBER_DOMAIN,
        service=SERVICE_SET_VALUE,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_VALUE: value,
        },
        blocking=True,
    )


async def set_target_temperature(hass: HomeAssistant, entity_id: str, temperature: float, /) -> None:
    """Set the target temperature of a climate or water heater entity with the action.

    The temperature is not written before `fire_debounced_writes()`.
    """
    # The water heater action has the same name and fields as the climate action.
    domain, _ = split_entity_id(entity_id)
    await hass.services.async_call(
        domain=domain,
        service=SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_TEMPERATURE: temperature,
        },
        blocking=True,
    )


async def fire_debounced_writes(hass: HomeAssistant, /) -> None:
    """Advance the time by the delay of the debounced writes and wait until they are written."""
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=FLASH_WRITE_DELAY))
    await hass.async_block_till_done()
