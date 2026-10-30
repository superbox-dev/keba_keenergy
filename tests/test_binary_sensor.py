# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the binary sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.const import STATE_OFF
from homeassistant.const import STATE_UNKNOWN
from homeassistant.const import Platform

from tests import get_platform_states
from tests import get_state
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import get_multiple_devices_responses
from tests.test_binary_sensor_data import COMPRESSOR_FAILURE_ENTITY_ID
from tests.test_binary_sensor_data import COMPRESSOR_FAILURE_MESSAGE_ID

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_binary_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all binary sensors."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE, has_passive_cooling="true")
    await fake_api.setup_integration()

    for state in get_platform_states(hass, config_entry, Platform.BINARY_SENSOR):
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
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    state: State = get_state(hass, COMPRESSOR_FAILURE_ENTITY_ID)
    assert state.state == expected


async def test_failure_input_in_use_again(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a failure input has a state again after the next update, once the control unit reports it in use."""
    fake_api.message_ids = {COMPRESSOR_FAILURE_MESSAGE_ID: 50}
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE, MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    fake_api.message_ids = {}
    await config_entry.runtime_data.async_refresh()

    state: State = get_state(hass, COMPRESSOR_FAILURE_ENTITY_ID)
    assert state.state == STATE_OFF
