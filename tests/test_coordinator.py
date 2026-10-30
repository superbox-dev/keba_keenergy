# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the data update coordinator."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import State
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from tests import get_state
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_WITHOUT_SOLAR_AND_HEATING_CIRCUITS_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE
from tests.api_data import SYSTEM_SOLAR_CIRCUIT_NUMBERS
from tests.api_data import get_multiple_devices_fixed_data_response
from tests.api_data import get_multiple_devices_responses
from tests.api_data import replace_values
from tests.test_coordinator_data import HEAT_CIRCUIT_ENTITY_ID
from tests.test_coordinator_data import HEAT_CIRCUIT_VALUE

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.keba_keenergy.coordinator import KebaKeEnergyDataUpdateCoordinator
    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.no_fail_on_keba_errors
async def test_update_authentication_error(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that rejected credentials during an update start the reauthentication flow."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    coordinator: KebaKeEnergyDataUpdateCoordinator = config_entry.runtime_data
    fake_api.responses = [HTTPStatus.UNAUTHORIZED]

    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert isinstance(coordinator.last_exception, ConfigEntryAuthFailed)
    assert coordinator.last_exception.translation_key == "authentication_error"
    assert [flow["context"]["source"] for flow in config_entry.async_get_active_flows(hass, {SOURCE_REAUTH})] == [
        SOURCE_REAUTH,
    ]


@pytest.mark.parametrize("error", [HTTPStatus.BAD_REQUEST, TimeoutError()], ids=["http_error", "timeout"])
@pytest.mark.no_fail_on_keba_errors
async def test_update_api_error(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    error: Exception | HTTPStatus,
) -> None:
    """Test that the entities are unavailable if an update fails or times out."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    coordinator: KebaKeEnergyDataUpdateCoordinator = config_entry.runtime_data
    fake_api.responses = [error]

    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert isinstance(coordinator.last_exception, UpdateFailed)
    assert coordinator.last_exception.translation_key == "communication_error"

    state: State | None = hass.states.get("sensor.keba_keenergy_12345678_outdoor_temperature")
    assert isinstance(state, State)
    assert state.state == STATE_UNAVAILABLE


@pytest.mark.no_fail_on_keba_errors
async def test_update_curves_error(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the update fails if the curves cannot be read after the values."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE, MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    coordinator: KebaKeEnergyDataUpdateCoordinator = config_entry.runtime_data
    fake_api.curves = HTTPStatus.BAD_REQUEST

    await coordinator.async_refresh()

    assert isinstance(coordinator.last_exception, UpdateFailed)
    assert coordinator.last_exception.translation_key == "communication_error"
    assert get_state(hass, "sensor.keba_keenergy_12345678_outdoor_temperature") == STATE_UNAVAILABLE


@pytest.mark.parametrize(
    "config_entry",
    [
        {"options": {"scan_interval_tick_heat_circuit": 2}},
    ],
    indirect=True,
    ids=["heat_circuit_every_second_tick"],
)
async def test_update_interval_ticks(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a device with an update multiplier of 2 is only requested every second update.

    A skipped endpoint keeps its values, the other endpoints are updated.
    """
    fake_api.responses = [
        replace_values(MULTIPLE_DEVICES_RESPONSE, SYSTEM_SOLAR_CIRCUIT_NUMBERS.read("0")),
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
        # The values of the heating circuits are skipped on this refresh.
        MULTIPLE_DEVICES_WITHOUT_SOLAR_AND_HEATING_CIRCUITS_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    coordinator: KebaKeEnergyDataUpdateCoordinator = config_entry.runtime_data
    heat_circuit_state: str = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)

    assert HEAT_CIRCUIT_VALUE in fake_api.read_requests()[-1]

    await coordinator.async_refresh()

    assert HEAT_CIRCUIT_VALUE in fake_api.read_requests()[-1]

    await coordinator.async_refresh()

    assert HEAT_CIRCUIT_VALUE not in fake_api.read_requests()[-1]
    assert get_state(hass, HEAT_CIRCUIT_ENTITY_ID) == heat_circuit_state
    assert get_state(hass, "sensor.keba_keenergy_12345678_buffer_tank_target_temperature_1") == "42.0"
    # The control unit has no solar circuit, so its values are never requested.
    assert not any("solarCircuit" in body for body in fake_api.read_requests())


@pytest.mark.parametrize(
    "config_entry",
    [
        {"options": {"scan_interval_tick_heat_circuit": 2}},
    ],
    indirect=True,
    ids=["heat_circuit_every_second_tick"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_update_interval_ticks_keep_message_ids(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a skipped device type keeps its message ids until it is requested again."""
    entity_id: str = "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_1"
    fake_api.message_ids = {"APPL.CtrlAppl.sParam.heatCircuit[0].tempRoom.state.msgId": 50}
    fake_api.responses = [
        replace_values(MULTIPLE_DEVICES_RESPONSE, SYSTEM_SOLAR_CIRCUIT_NUMBERS.read("0")),
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
        # The values of the heating circuits are skipped on this refresh.
        MULTIPLE_DEVICES_WITHOUT_SOLAR_AND_HEATING_CIRCUITS_DATA_RESPONSE,
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    coordinator: KebaKeEnergyDataUpdateCoordinator = config_entry.runtime_data

    # The heating circuits are requested on the first and the third refresh.
    await coordinator.async_refresh()

    assert get_state(hass, entity_id) == STATE_UNKNOWN

    fake_api.message_ids = {}
    await coordinator.async_refresh()

    assert get_state(hass, entity_id) == STATE_UNKNOWN

    await coordinator.async_refresh()

    assert get_state(hass, entity_id) == "22.418831"
