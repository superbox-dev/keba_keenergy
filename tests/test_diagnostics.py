# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_SSL
from homeassistant.const import CONF_USERNAME
from pytest_homeassistant_custom_component.components.diagnostics import get_diagnostics_for_config_entry

from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from pytest_homeassistant_custom_component.typing import ClientSessionGenerator
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    "config_entry",
    [{"data": {CONF_HOST: "10.0.0.100", CONF_SSL: False, CONF_USERNAME: "test", CONF_PASSWORD: "test"}}],
    indirect=True,
    ids=["with_credentials"],
)
async def test_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the diagnostics of a config entry, without the credentials, the host and the serial number."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    assert await get_diagnostics_for_config_entry(hass, hass_client, config_entry) == snapshot
