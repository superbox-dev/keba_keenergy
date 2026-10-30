# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the data update coordinator."""

from __future__ import annotations

import json
from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import State
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_WITHOUT_SOLAR_AND_HEATING_CIRCUITS_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE
from tests.api_data import SYSTEM_BUFFER_TANK_NUMBERS
from tests.api_data import SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS
from tests.api_data import SYSTEM_HEAT_CIRCUIT_NUMBERS
from tests.api_data import SYSTEM_HEAT_PUMP_NUMBERS
from tests.api_data import SYSTEM_HOT_WATER_TANK_NUMBERS
from tests.api_data import SYSTEM_SOLAR_CIRCUIT_NUMBERS
from tests.api_data import SYSTEM_SWITCH_VALVE_NUMBERS
from tests.api_data import get_multiple_devices_fixed_data_response

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
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
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
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
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


@pytest.mark.parametrize(
    "config_entry",
    [
        {
            "options": {
                "scan_interval": 20,
                "scan_interval_tick_system": 1,
                "scan_interval_tick_heat_pump": 1,
                "scan_interval_tick_heat_circuit": 2,
                "scan_interval_tick_solar_circuit": 1,
                "scan_interval_tick_hot_water_tank": 1,
                "scan_interval_tick_buffer_tank": 1,
                "scan_interval_tick_switch_valve": 1,
                "scan_interval_tick_external_heat_source": 1,
            },
        },
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

    A skipped section keeps its values, the other sections are updated.
    """
    fake_api.responses = [
        [
            json.loads(SYSTEM_HEAT_PUMP_NUMBERS % "1"),
            json.loads(SYSTEM_HEAT_CIRCUIT_NUMBERS % "2"),
            json.loads(SYSTEM_SOLAR_CIRCUIT_NUMBERS % "0"),
            json.loads(SYSTEM_BUFFER_TANK_NUMBERS % "2"),
            json.loads(SYSTEM_HOT_WATER_TANK_NUMBERS % "2"),
            json.loads(SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS % "2"),
            json.loads(SYSTEM_SWITCH_VALVE_NUMBERS % "2"),
        ],
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
        # The values of the heating circuits are skipped on this refresh.
        MULTIPLE_DEVICES_WITHOUT_SOLAR_AND_HEATING_CIRCUITS_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    coordinator: KebaKeEnergyDataUpdateCoordinator = config_entry.runtime_data
    heat_circuit_reads: list[int] = [_heat_circuit_reads(fake_api)]
    heat_circuit_state: str = _state(hass, "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_1")

    for _ in range(2):
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
        await coordinator.async_request_refresh()
        await hass.async_block_till_done()
        heat_circuit_reads.append(_heat_circuit_reads(fake_api))

    assert heat_circuit_reads == [1, 2, 2]
    assert _state(hass, "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_1") == heat_circuit_state
    assert _state(hass, "sensor.keba_keenergy_12345678_buffer_tank_target_temperature_1") == "42.0"
    # The control unit has no solar circuit, so its values are never requested.
    assert not any("solarCircuit" in body for body in fake_api.read_requests())


@pytest.mark.parametrize(
    "config_entry",
    [
        {
            "options": {
                "scan_interval": 20,
                "scan_interval_tick_system": 1,
                "scan_interval_tick_heat_pump": 1,
                "scan_interval_tick_heat_circuit": 2,
                "scan_interval_tick_solar_circuit": 1,
                "scan_interval_tick_hot_water_tank": 1,
                "scan_interval_tick_buffer_tank": 1,
                "scan_interval_tick_switch_valve": 1,
                "scan_interval_tick_external_heat_source": 1,
            },
        },
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
    """Test that a skipped section keeps its message ids until it is requested again."""
    entity_id: str = "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_1"
    fake_api.message_ids = {"APPL.CtrlAppl.sParam.heatCircuit[0].tempRoom.state.msgId": 50}
    fake_api.responses = [
        [
            json.loads(SYSTEM_HEAT_PUMP_NUMBERS % "1"),
            json.loads(SYSTEM_HEAT_CIRCUIT_NUMBERS % "2"),
            json.loads(SYSTEM_SOLAR_CIRCUIT_NUMBERS % "0"),
            json.loads(SYSTEM_BUFFER_TANK_NUMBERS % "2"),
            json.loads(SYSTEM_HOT_WATER_TANK_NUMBERS % "2"),
            json.loads(SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS % "2"),
            json.loads(SYSTEM_SWITCH_VALVE_NUMBERS % "2"),
        ],
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
        # The values of the heating circuits are skipped on this refresh.
        MULTIPLE_DEVICES_WITHOUT_SOLAR_AND_HEATING_CIRCUITS_DATA_RESPONSE,
        MULTIPLE_DEVICES_WITHOUT_SOLAR_CIRCUITS_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    coordinator: KebaKeEnergyDataUpdateCoordinator = config_entry.runtime_data
    states: list[str] = []

    # The heating circuits are requested on the first and the third refresh.
    for message_ids in ({"APPL.CtrlAppl.sParam.heatCircuit[0].tempRoom.state.msgId": 50}, {}, {}):
        fake_api.message_ids = message_ids
        await coordinator.async_refresh()
        await hass.async_block_till_done()

        state: State | None = hass.states.get(entity_id)
        assert isinstance(state, State)
        states.append(state.state)

    assert states == [STATE_UNKNOWN, STATE_UNKNOWN, "22.418831"]


def _heat_circuit_reads(fake_api: FakeKebaKeEnergyAPI) -> int:
    """Return the number of read requests with the values of the heating circuits."""
    return sum('"APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode"' in body for body in fake_api.read_requests())


def _state(hass: HomeAssistant, entity_id: str, /) -> str:
    """Return the state of an entity, which must not be unavailable."""
    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)
    assert state.state != STATE_UNAVAILABLE
    return state.state
