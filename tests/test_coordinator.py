# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the data update coordinator."""

from __future__ import annotations

import json
from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.util import dt as dt_util
from keba_keenergy_api.constants import SectionPrefix
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from tests.api_data import HEATING_CURVE_NAMES_RESPONSE
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_3_1
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_3_2
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import SYSTEM_BUFFER_TANK_NUMBERS
from tests.api_data import SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS
from tests.api_data import SYSTEM_HEAT_CIRCUIT_NUMBERS
from tests.api_data import SYSTEM_HEAT_PUMP_NUMBERS
from tests.api_data import SYSTEM_HOT_WATER_TANK_NUMBERS
from tests.api_data import SYSTEM_SOLAR_CIRCUIT_NUMBERS
from tests.api_data import SYSTEM_SWITCH_VALVE_NUMBERS
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

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
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
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
)
async def test_update_interval_ticks(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test that a device with an update multiplier of 2 is only requested every second update."""
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
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_3_2,
        *HEATING_CURVES_RESPONSE_1_1,
        MULTIPLE_POSITION_DATA_RESPONSE_3_2,
        *HEATING_CURVES_RESPONSE_1_1,
        MULTIPLE_POSITION_DATA_RESPONSE_3_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]

    await fake_api.setup_integration()

    coordinator: KebaKeEnergyDataUpdateCoordinator = config_entry.runtime_data

    assert not coordinator.request_data_groups.get(SectionPrefix.SOLAR_CIRCUIT)
    heat_circuit_reads: list[int] = [_heat_circuit_reads(fake_api)]

    assert coordinator.data == snapshot

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
    await coordinator.async_request_refresh()
    await hass.async_block_till_done()

    heat_circuit_reads.append(_heat_circuit_reads(fake_api))

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
    await coordinator.async_request_refresh()
    await hass.async_block_till_done()

    heat_circuit_reads.append(_heat_circuit_reads(fake_api))

    assert heat_circuit_reads == [1, 2, 2]

    assert coordinator.data == snapshot


def _heat_circuit_reads(fake_api: FakeKebaKeEnergyAPI) -> int:
    """Return the number of read requests with the values of the heating circuits."""
    return sum('"APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode"' in body for body in fake_api.read_requests())
