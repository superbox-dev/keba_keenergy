# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the KEBA KeEnergy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.core import State
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.translation import async_get_translations

from custom_components.keba_keenergy.const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.const import Platform
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry


async def setup_integration(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    """Set up the KEBA KeEnergy integration in Home Assistant."""
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


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


async def get_option_translations(hass: HomeAssistant, state: State, /) -> dict[str, str]:
    """Return the translated options of an entity with options (an enum sensor or a select)."""
    entry: er.RegistryEntry | None = er.async_get(hass).async_get(state.entity_id)
    assert entry is not None
    translations: dict[str, str] = await init_translations(hass, category="entity")

    return {
        option: translations[f"component.keba_keenergy.entity.{entry.domain}.{entry.translation_key}.state.{option}"]
        for option in state.attributes[ATTR_OPTIONS]
    }
