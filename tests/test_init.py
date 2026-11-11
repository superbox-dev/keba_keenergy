# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the setup of the integration."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_SSL
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.keba_keenergy.const import DOMAIN
from tests import get_flows_in_progress
from tests.api_data import ENTRY_ID
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import NOW
from tests.api_data import SINGLE_DEVICE_DATA_RESPONSE
from tests.api_data import ReadResponse
from tests.api_data import get_multiple_devices_responses
from tests.api_data import get_single_device_responses

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests import FlowInProgress
    from tests.conftest import FakeKebaKeEnergyAPI

pytestmark = pytest.mark.freeze_time(NOW)


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_load_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test setting up the integration."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE, has_passive_cooling="true")
    await fake_api.setup_integration()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    assert set(hass.states.async_entity_ids()) == snapshot


async def test_load_unload_config_entry(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test that the config entry is loaded and unloaded."""
    assert init_integration.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(ENTRY_ID)
    await hass.async_block_till_done()

    assert init_integration.state is ConfigEntryState.NOT_LOADED


async def test_entities_disabled_by_default(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the entities that the integration disables by default, they have no state."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE, has_passive_cooling="true")
    await fake_api.setup_integration()

    disabled_entity_ids: list[str] = sorted(
        entry.entity_id
        for entry in er.async_entries_for_config_entry(entity_registry, ENTRY_ID)
        if entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
    )

    assert disabled_entity_ids == snapshot
    assert not set(disabled_entity_ids) & set(hass.states.async_entity_ids())


@pytest.mark.parametrize(
    "responses",
    [
        get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE, has_passive_cooling="true"),
        get_single_device_responses(SINGLE_DEVICE_DATA_RESPONSE),
    ],
    ids=["multiple_devices", "single_device"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_devices(
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    fake_api: FakeKebaKeEnergyAPI,
    responses: list[ReadResponse],
    snapshot: SnapshotAssertion,
) -> None:
    """Test the devices that the integration creates, every entity belongs to one of them.

    The devices are compared with their translated names and the device they belong to.
    """
    fake_api.responses = list(responses)
    await fake_api.setup_integration()

    devices: dict[str, dr.DeviceEntry] = {
        identifier: device
        for device in dr.async_entries_for_config_entry(device_registry, ENTRY_ID)
        for _, identifier in device.identifiers
    }
    # The snapshot of a device replaces the ID of the device it belongs to, so its identifier is compared as well.
    identifiers: dict[str, str] = {device.id: identifier for identifier, device in devices.items()}
    via_devices: dict[str, str | None] = {
        identifier: identifiers.get(device.via_device_id or "") for identifier, device in sorted(devices.items())
    }

    assert sorted(devices) == snapshot(name="identifiers")
    assert via_devices == snapshot(name="via_devices")

    for identifier, device in sorted(devices.items()):
        assert device == snapshot(name=identifier)

    assert {entry.device_id for entry in er.async_entries_for_config_entry(entity_registry, ENTRY_ID)} == {
        device.id for device in devices.values()
    }


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_remove_stale_devices(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that devices which the control unit no longer provides are removed, with their entities."""
    mock_config_entry.add_to_hass(hass)
    stale_device: dr.DeviceEntry = device_registry.async_get_or_create(
        config_entry_id=ENTRY_ID,
        identifiers={(DOMAIN, "12345678_buffer_tank_3")},
    )
    stale_entity: er.RegistryEntry = entity_registry.async_get_or_create(
        SENSOR_DOMAIN,
        DOMAIN,
        "12345678_buffer_tank_current_top_temperature_3",
        config_entry=mock_config_entry,
        device_id=stale_device.id,
    )
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    assert device_registry.async_get(stale_device.id) is None
    assert entity_registry.async_get(stale_entity.entity_id) is None

    assert "12345678_buffer_tank_1" in {
        identifier
        for device in dr.async_entries_for_config_entry(device_registry, ENTRY_ID)
        for _, identifier in device.identifiers
    }


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (HTTPStatus.BAD_REQUEST, (ConfigEntryState.SETUP_RETRY, "communication_error", [])),
        (TimeoutError(), (ConfigEntryState.SETUP_RETRY, "communication_error", [])),
        (
            HTTPStatus.UNAUTHORIZED,
            (
                ConfigEntryState.SETUP_ERROR,
                "authentication_error",
                [("reauth_confirm", DOMAIN, SOURCE_REAUTH, ENTRY_ID)],
            ),
        ),
    ],
    ids=["http_error", "timeout", "authentication_error"],
)
@pytest.mark.no_fail_on_keba_errors
async def test_setup_failed(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    error: Exception | HTTPStatus,
    expected: tuple[ConfigEntryState, str, list[FlowInProgress]],
) -> None:
    """Test that a failed setup is retried, or starts the reauthentication for rejected credentials."""
    fake_api.responses = [error]
    fake_api.register_requests(mock_config_entry.data[CONF_HOST], ssl=mock_config_entry.data[CONF_SSL])
    mock_config_entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(ENTRY_ID)
    await hass.async_block_till_done()

    assert (
        mock_config_entry.state,
        mock_config_entry.error_reason_translation_key,
        get_flows_in_progress(hass),
    ) == expected
