# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the diagnostics."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from typing import Any

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_SSL
from homeassistant.const import CONF_USERNAME
from pytest_homeassistant_custom_component.components.diagnostics import get_diagnostics_for_config_entry

from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import get_multiple_devices_responses

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
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    diagnostics: dict[str, Any] = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)

    assert diagnostics == snapshot
    # Also a value added to the diagnostics later must not contain the serial number or the host.
    assert "12345678" not in json.dumps(diagnostics)
    assert "10.0.0.100" not in json.dumps(diagnostics)
