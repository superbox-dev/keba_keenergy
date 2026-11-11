# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the icon translations."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.icon import async_get_icons

from custom_components.keba_keenergy.const import DOMAIN
from tests import get_multiple_devices_responses
from tests.const import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.const import MULTIPLE_DEVICES_PASSIVE_COOLING_FIXED_DATA_RESPONSE
from tests.const import NOW

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI

pytestmark = pytest.mark.freeze_time(NOW)


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_icons(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test that every icon in icons.json is used and the icons that the entities get."""
    fake_api.responses = get_multiple_devices_responses(
        MULTIPLE_DEVICES_DATA_RESPONSE, fixed_data=MULTIPLE_DEVICES_PASSIVE_COOLING_FIXED_DATA_RESPONSE
    )
    await fake_api.setup_integration()

    icons: dict[str, dict[str, Any]] = (await async_get_icons(hass, "entity", [DOMAIN]))[DOMAIN]
    entries: list[er.RegistryEntry] = er.async_entries_for_config_entry(
        entity_registry,
        mock_config_entry.entry_id,
    )

    used: set[tuple[str, str | None]] = {(entry.domain, entry.translation_key) for entry in entries}
    defined: set[tuple[str, str | None]] = {(platform, key) for platform, keys in icons.items() for key in keys}

    assert defined - used == set()
    assert {
        entry.entity_id: icons.get(entry.domain, {}).get(entry.translation_key or "") or entry.original_icon
        for entry in sorted(entries, key=lambda entry: entry.entity_id)
    } == snapshot
