# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the event entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.const import Platform

from tests import get_platform_states
from tests.api_data import get_single_device_responses

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_events(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all event entities."""
    fake_api.responses = get_single_device_responses()
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.EVENT):
        assert state == snapshot(name=state.entity_id)
