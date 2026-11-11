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
from pytest_homeassistant.components.diagnostics import get_diagnostics_for_config_entry

from tests.api_data import NOW

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant.common import MockConfigEntry
    from pytest_homeassistant.typing import ClientSessionGenerator
    from syrupy.assertion import SnapshotAssertion

pytestmark = pytest.mark.freeze_time(NOW)


@pytest.mark.parametrize(
    "entry_data",
    [{CONF_HOST: "10.0.0.100", CONF_SSL: False, CONF_USERNAME: "test", CONF_PASSWORD: "test"}],
    ids=["with_credentials"],
)
async def test_diagnostics(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    hass_client: ClientSessionGenerator,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the diagnostics of a config entry, without the credentials, the host and the serial number."""
    diagnostics: dict[str, Any] = await get_diagnostics_for_config_entry(hass, hass_client, init_integration)

    assert diagnostics == snapshot
    # Also a value added to the diagnostics later must not contain the serial number or the host.
    assert "12345678" not in json.dumps(diagnostics)
    assert "10.0.0.100" not in json.dumps(diagnostics)
