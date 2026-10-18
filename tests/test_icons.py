# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the icon translations."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.icon import async_get_icons

from custom_components.keba_keenergy.const import DOMAIN
from tests.api_data import HEATING_CURVE_NAMES_RESPONSE
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_icons(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test that every icon in icons.json is used and the icons that the entities get."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    await fake_api.setup_integration()

    icons: dict[str, dict[str, Any]] = (await async_get_icons(hass, "entity", [DOMAIN]))[DOMAIN]
    entries: list[er.RegistryEntry] = er.async_entries_for_config_entry(
        er.async_get(hass),
        fake_api.config_entry.entry_id,
    )

    used: set[tuple[str, str | None]] = {(entry.domain, entry.translation_key) for entry in entries}
    defined: set[tuple[str, str | None]] = {(platform, key) for platform, keys in icons.items() for key in keys}

    assert defined - used == set()
    assert {
        entry.entity_id: icons.get(entry.domain, {}).get(entry.translation_key or "") or entry.original_icon
        for entry in sorted(entries, key=lambda entry: entry.entity_id)
    } == snapshot
