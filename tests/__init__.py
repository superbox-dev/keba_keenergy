# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the KEBA KeEnergy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import State
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.translation import async_get_translations

from custom_components.keba_keenergy.const import DOMAIN

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


def get_state(hass: HomeAssistant, entity_id: str, /) -> str:
    """Return the state of an entity, which must exist."""
    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)
    return state.state


async def get_option_translations(hass: HomeAssistant, state: State, /) -> dict[str, str]:
    """Return the translated options of an entity with options (an enum sensor or a select)."""
    entry: er.RegistryEntry | None = er.async_get(hass).async_get(state.entity_id)
    assert entry is not None
    translations: dict[str, str] = await init_translations(hass, category="entity")

    return {
        option: translations[f"component.keba_keenergy.entity.{entry.domain}.{entry.translation_key}.state.{option}"]
        for option in state.attributes[ATTR_OPTIONS]
    }


async def select_option(hass: HomeAssistant, entity_id: str, option: str, /) -> None:
    """Select the option of a select entity with the action."""
    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_OPTION: option,
        },
        blocking=True,
    )
