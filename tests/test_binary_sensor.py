from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.core import State

from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import HEATING_CURVE_NAMES_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from pytest_homeassistant_custom_component.common import MockConfigEntry
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
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_hot_water_flow_2",
        # heat pump
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_compressor_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_actuator_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_pressure_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_three_phase_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_vfd_failure",
        "binary_sensor.keba_keenergy_12345678_heat_pump_heat_request",
        # solar circuit
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_1",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_2",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_1",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_2",
        # external heat source
        "binary_sensor.keba_keenergy_12345678_external_heat_source_heat_request_1",
        "binary_sensor.keba_keenergy_12345678_external_heat_source_heat_request_2",
    ],
)
@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_binary_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    language: str,
    entity: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])
    hass.config.language = language

    await setup_integration(hass, config_entry)

    _entity: State | None = hass.states.get(entity)
    assert isinstance(_entity, State)
    assert _entity == snapshot
