# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the binary sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.core import State

from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    "entity",
    [
        # buffer tank
        "binary_sensor.keba_keenergy_12345678_buffer_tank_cool_request_1",
        "binary_sensor.keba_keenergy_12345678_buffer_tank_cool_request_2",
        "binary_sensor.keba_keenergy_12345678_buffer_tank_heat_request_1",
        "binary_sensor.keba_keenergy_12345678_buffer_tank_heat_request_2",
        # hot water tank
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_circulation_pump_state_1",
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_circulation_pump_state_2",
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_heat_request_1",
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_heat_request_2",
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_hot_water_flow_1",
        # heat pump
        "binary_sensor.keba_keenergy_12345678_heat_pump_consuming_excess_energy",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_compressor_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_actuator_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_pressure_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_three_phase_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_vfd_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_heat_request",
        # heating circuit
        "binary_sensor.keba_keenergy_12345678_heat_circuit_pump_state_1",
        # solar circuit
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_1",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_2",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_1",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_2",
        # external heat source
        "binary_sensor.keba_keenergy_12345678_external_heat_source_consuming_excess_energy_1",
        "binary_sensor.keba_keenergy_12345678_external_heat_source_consuming_excess_energy_2",
        "binary_sensor.keba_keenergy_12345678_external_heat_source_heat_request_1",
        "binary_sensor.keba_keenergy_12345678_external_heat_source_heat_request_2",
        # photovoltaics
        "binary_sensor.keba_keenergy_12345678_photovoltaics_excess_energy_active",
    ],
)
@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_binary_sensors(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    entity: str,
) -> None:
    """Test the states of the binary sensors."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]

    await fake_api.setup_integration()

    _entity: State | None = hass.states.get(entity)
    assert isinstance(_entity, State)
    assert _entity == snapshot
