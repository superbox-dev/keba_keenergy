# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er

from tests import get_option_translations
from tests import get_platform_states
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_sensors(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all sensors and the translated options of the enum sensors."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.SENSOR):
        assert state == snapshot(name=state.entity_id)

        if ATTR_OPTIONS in state.attributes:
            assert await get_option_translations(hass, state) == snapshot(name=f"{state.entity_id}_options")


@pytest.mark.parametrize(
    "entity_id",
    [
        "sensor.keba_keenergy_12345678_heat_pump_operating_time",
        "sensor.keba_keenergy_12345678_photovoltaics_daily_energy",
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_converted_sensor_display_precision(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
) -> None:
    """Test that converted sensors keep the exact value and are displayed with two decimals."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    entry: er.RegistryEntry | None = er.async_get(hass).async_get(entity_id)
    assert entry is not None
    assert entry.options["sensor"] == {"suggested_display_precision": 2}
