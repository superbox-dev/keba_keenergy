# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the binary sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.const import STATE_OFF
from homeassistant.const import STATE_UNKNOWN
from homeassistant.const import Platform
from homeassistant.core import State

from tests import get_platform_states
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response
from tests.test_binary_sensor_data import COMPRESSOR_FAILURE_ENTITY_ID
from tests.test_binary_sensor_data import COMPRESSOR_FAILURE_MESSAGE_ID

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from syrupy.assertion import SnapshotAssertion

    from custom_components.keba_keenergy.coordinator import KebaKeEnergyDataUpdateCoordinator
    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize("language", ["en", "de"], indirect=True, ids=["en", "de"])
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


@pytest.mark.parametrize(
    ("message_id", "expected"), [(0, STATE_OFF), (50, STATE_UNKNOWN)], ids=["confirmed", "unconfirmed"]
)
async def test_failure_input_not_in_use(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    message_id: int,
    expected: str,
) -> None:
    """Test that a failure input is unknown if the control unit reports it as not in use (message id not 0)."""
    fake_api.message_ids = {COMPRESSOR_FAILURE_MESSAGE_ID: message_id}
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    state: State | None = hass.states.get(COMPRESSOR_FAILURE_ENTITY_ID)
    assert isinstance(state, State)
    assert state.state == expected


async def test_failure_input_in_use_again(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a failure input has a state again after the next update, once the control unit reports it in use."""
    fake_api.message_ids = {COMPRESSOR_FAILURE_MESSAGE_ID: 50}
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    fake_api.message_ids = {}
    coordinator: KebaKeEnergyDataUpdateCoordinator = fake_api.config_entry.runtime_data
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    state: State | None = hass.states.get(COMPRESSOR_FAILURE_ENTITY_ID)
    assert isinstance(state, State)
    assert state.state == STATE_OFF
