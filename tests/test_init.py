# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the setup of the integration."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_SSL
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.keba_keenergy.const import DOMAIN
from tests.api_data import DEFAULT_POSITION_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_FIXED_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_load_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test setting up the integration."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    assert config_entry.state is ConfigEntryState.LOADED

    assert set(hass.states.async_entity_ids()) == snapshot


@pytest.mark.parametrize(
    "config_entry",
    [
        (
            {
                "title": "KEBA KeEnergy (ap4400.local)",
                "data": {
                    CONF_HOST: "ap4400.local",
                    CONF_SSL: False,
                },
                "unique_id": "12345678",
            }
        ),
    ],
    indirect=["config_entry"],
)
async def test_unload_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test unloading the integration."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    assert config_entry.state == ConfigEntryState.LOADED
    await hass.config_entries.async_unload(config_entry.entry_id)
    assert config_entry.state == ConfigEntryState.NOT_LOADED


@pytest.mark.parametrize(
    "response",
    [
        [
            MULTIPLE_POSITIONS_RESPONSE,
            get_multiple_position_fixed_data_response(has_passive_cooling="true"),
            MULTIPLE_POSITION_DATA_RESPONSE,
        ],
        [
            DEFAULT_POSITION_RESPONSE,
            DEFAULT_POSITION_FIXED_DATA_RESPONSE,
            DEFAULT_POSITION_DATA_RESPONSE,
        ],
    ],
    ids=["multiple_positions", "default_position"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_devices(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    response: list[list[dict[str, Any]]],
    snapshot: SnapshotAssertion,
) -> None:
    """Test the devices that the integration creates."""
    fake_api.responses = [*response]
    await fake_api.setup_integration()

    assert (
        sorted(
            identifier
            for device in dr.async_entries_for_config_entry(dr.async_get(hass), fake_api.config_entry.entry_id)
            for _, identifier in device.identifiers
        )
        == snapshot
    )


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_remove_stale_devices(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that devices which the control unit no longer provides are removed, with their entities."""
    config_entry.add_to_hass(hass)
    device_registry: dr.DeviceRegistry = dr.async_get(hass)
    entity_registry: er.EntityRegistry = er.async_get(hass)
    stale_device: dr.DeviceEntry = device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, "12345678_buffer_tank_3")},
    )
    stale_entity: er.RegistryEntry = entity_registry.async_get_or_create(
        "sensor",
        DOMAIN,
        "12345678_buffer_tank_current_top_temperature_3",
        config_entry=config_entry,
        device_id=stale_device.id,
    )
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST], ssl=config_entry.data[CONF_SSL])
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert device_registry.async_get(stale_device.id) is None
    assert entity_registry.async_get(stale_entity.entity_id) is None

    assert "12345678_buffer_tank_1" in {
        identifier
        for device in dr.async_entries_for_config_entry(device_registry, config_entry.entry_id)
        for _, identifier in device.identifiers
    }
