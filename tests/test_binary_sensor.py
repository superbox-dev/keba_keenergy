# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the binary sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.const import Platform

from tests import get_platform_states
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_binary_sensors(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all binary sensors."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.BINARY_SENSOR):
        assert state == snapshot(name=state.entity_id)
