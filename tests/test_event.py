# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the event entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.const import Platform
from pytest_homeassistant.common import snapshot_platform

from tests.api_data import ENTRY_ID
from tests.api_data import NOW
from tests.api_data import get_single_device_responses

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers import entity_registry as er
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI

pytestmark = pytest.mark.freeze_time(NOW)


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_events(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all event entities."""
    fake_api.platforms = [Platform.EVENT]
    fake_api.responses = get_single_device_responses()
    await fake_api.setup_integration()

    await snapshot_platform(hass, entity_registry, snapshot, ENTRY_ID)
