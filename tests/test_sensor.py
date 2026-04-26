from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.core import State

from tests import init_translations
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
        # system
        "sensor.keba_keenergy_12345678_control_cpu_usage",
        "sensor.keba_keenergy_12345678_cpu_usage",
        "sensor.keba_keenergy_12345678_free_ram",
        "sensor.keba_keenergy_12345678_operating_mode",
        "sensor.keba_keenergy_12345678_outdoor_temperature",
        "sensor.keba_keenergy_12345678_ram_usage",
        "sensor.keba_keenergy_12345678_webserver_cpu_usage",
        "sensor.keba_keenergy_12345678_webview_cpu_usage",
        # buffer tank
        "sensor.keba_keenergy_12345678_buffer_tank_current_bottom_temperature_1",
        "sensor.keba_keenergy_12345678_buffer_tank_current_bottom_temperature_2",
        "sensor.keba_keenergy_12345678_buffer_tank_current_top_temperature_1",
        "sensor.keba_keenergy_12345678_buffer_tank_current_top_temperature_2",
        "sensor.keba_keenergy_12345678_buffer_tank_excess_energy_mode_1",
        "sensor.keba_keenergy_12345678_buffer_tank_excess_energy_mode_2",
        "sensor.keba_keenergy_12345678_buffer_tank_excess_energy_target_temperature_1",
        "sensor.keba_keenergy_12345678_buffer_tank_excess_energy_target_temperature_2",
        "sensor.keba_keenergy_12345678_buffer_tank_operating_mode_1",
        "sensor.keba_keenergy_12345678_buffer_tank_operating_mode_2",
        "sensor.keba_keenergy_12345678_buffer_tank_standby_temperature_1",
        "sensor.keba_keenergy_12345678_buffer_tank_standby_temperature_2",
        "sensor.keba_keenergy_12345678_buffer_tank_target_temperature_1",
        "sensor.keba_keenergy_12345678_buffer_tank_target_temperature_2",
        # hot water tank
        "sensor.keba_keenergy_12345678_hot_water_tank_circulation_return_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_circulation_return_temperature_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_current_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_current_temperature_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_excess_energy_mode_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_excess_energy_mode_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_excess_energy_target_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_excess_energy_target_temperature_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_fresh_water_module_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_standby_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_standby_temperature_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_target_temperature_2",
        # heat pump
        "sensor.keba_keenergy_12345678_heat_pump_activation_counter",
        "sensor.keba_keenergy_12345678_heat_pump_circulation_pump",
        "sensor.keba_keenergy_12345678_heat_pump_compressor",
        "sensor.keba_keenergy_12345678_heat_pump_compressor_input_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_compressor_output_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_compressor_power",
        "sensor.keba_keenergy_12345678_heat_pump_condenser_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_cooling_energy",
        "sensor.keba_keenergy_12345678_heat_pump_cooling_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_cooling_excess_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_cooling_spf",
        "sensor.keba_keenergy_12345678_heat_pump_cop",
        "sensor.keba_keenergy_12345678_heat_pump_current_overheating",
        "sensor.keba_keenergy_12345678_heat_pump_excess_energy_activation_counter",
        "sensor.keba_keenergy_12345678_heat_pump_excess_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_excess_energy_max_runtime",
        "sensor.keba_keenergy_12345678_heat_pump_excess_energy_operating_time",
        "sensor.keba_keenergy_12345678_heat_pump_expansion_valve_position",
        "sensor.keba_keenergy_12345678_heat_pump_flow_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_heating_energy",
        "sensor.keba_keenergy_12345678_heat_pump_heating_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_heating_excess_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_heating_power",
        "sensor.keba_keenergy_12345678_heat_pump_heating_spf",
        "sensor.keba_keenergy_12345678_heat_pump_high_pressure",
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_energy",
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_excess_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_power",
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_spf",
        "sensor.keba_keenergy_12345678_heat_pump_low_pressure",
        "sensor.keba_keenergy_12345678_heat_pump_max_runtime",
        "sensor.keba_keenergy_12345678_heat_pump_operating_time",
        "sensor.keba_keenergy_12345678_heat_pump_return_flow_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_source_input_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_source_output_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_source_pump_speed",
        "sensor.keba_keenergy_12345678_heat_pump_state",
        "sensor.keba_keenergy_12345678_heat_pump_substate",
        "sensor.keba_keenergy_12345678_heat_pump_target_overheating",
        "sensor.keba_keenergy_12345678_heat_pump_total_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_total_spf",
        "sensor.keba_keenergy_12345678_heat_pump_total_thermal_energy",
        "sensor.keba_keenergy_12345678_heat_pump_vaporizer_temperature",
        # passive cooling
        "sensor.keba_keenergy_12345678_passive_cooling_circulation_pump_speed",
        "sensor.keba_keenergy_12345678_passive_cooling_mixer_flow_temperature",
        "sensor.keba_keenergy_12345678_passive_cooling_mixer_position",
        "sensor.keba_keenergy_12345678_passive_cooling_mixer_target_temperature",
        "sensor.keba_keenergy_12345678_passive_cooling_switch_valve_position",
        "sensor.keba_keenergy_12345678_passive_cooling_temperature",
        # heating circuit
        "sensor.keba_keenergy_12345678_heat_circuit_cool_request_2",
        "sensor.keba_keenergy_12345678_heat_circuit_cooling_curve_2",
        "sensor.keba_keenergy_12345678_heat_circuit_cooling_limit_day_2",
        "sensor.keba_keenergy_12345678_heat_circuit_cooling_limit_night_2",
        "sensor.keba_keenergy_12345678_heat_circuit_dew_point_1",
        "sensor.keba_keenergy_12345678_heat_circuit_excess_energy_cooling_limit_day_2",
        "sensor.keba_keenergy_12345678_heat_circuit_excess_energy_cooling_limit_night_2",
        "sensor.keba_keenergy_12345678_heat_circuit_excess_energy_heating_limit_day_1",
        "sensor.keba_keenergy_12345678_heat_circuit_excess_energy_heating_limit_night_1",
        "sensor.keba_keenergy_12345678_heat_circuit_excess_energy_mode_1",
        "sensor.keba_keenergy_12345678_heat_circuit_excess_energy_mode_2",
        "sensor.keba_keenergy_12345678_heat_circuit_excess_energy_target_cooling_temperature_2",
        "sensor.keba_keenergy_12345678_heat_circuit_excess_energy_target_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_setpoint_1",
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_setpoint_2",
        "sensor.keba_keenergy_12345678_heat_circuit_heat_request_1",
        "sensor.keba_keenergy_12345678_heat_circuit_heating_curve_1",
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_day_1",
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_night_1",
        "sensor.keba_keenergy_12345678_heat_circuit_mixer_position_1",
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1",
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_2",
        "sensor.keba_keenergy_12345678_heat_circuit_pump_speed_1",
        "sensor.keba_keenergy_12345678_heat_circuit_return_flow_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_room_humidity_1",
        "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_selected_target_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_selected_target_temperature_2",
        "sensor.keba_keenergy_12345678_heat_circuit_target_cooling_temperature_day_2",
        "sensor.keba_keenergy_12345678_heat_circuit_target_cooling_temperature_night_2",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_2",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_away_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_night_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_offset_2",
        # solar circuit
        "sensor.keba_keenergy_12345678_solar_circuit_actual_power_1",
        "sensor.keba_keenergy_12345678_solar_circuit_actual_power_2",
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_1",
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_2",
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_1",
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_2",
        "sensor.keba_keenergy_12345678_solar_circuit_daily_energy_1",
        "sensor.keba_keenergy_12345678_solar_circuit_daily_energy_2",
        "sensor.keba_keenergy_12345678_solar_circuit_heating_energy_1",
        "sensor.keba_keenergy_12345678_solar_circuit_heating_energy_2",
        "sensor.keba_keenergy_12345678_solar_circuit_pump_1_1",
        "sensor.keba_keenergy_12345678_solar_circuit_pump_1_2",
        "sensor.keba_keenergy_12345678_solar_circuit_pump_2_1",
        "sensor.keba_keenergy_12345678_solar_circuit_pump_2_2",
        "sensor.keba_keenergy_12345678_solar_circuit_source_temperature_1",
        "sensor.keba_keenergy_12345678_solar_circuit_source_temperature_2",
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_1_1",
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_1_2",
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_2_1",
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_2_2",
        # external heat source
        "sensor.keba_keenergy_12345678_external_heat_source_activation_counter_1",
        "sensor.keba_keenergy_12345678_external_heat_source_activation_counter_2",
        "sensor.keba_keenergy_12345678_external_heat_source_excess_energy_activation_counter_1",
        "sensor.keba_keenergy_12345678_external_heat_source_excess_energy_activation_counter_2",
        "sensor.keba_keenergy_12345678_external_heat_source_excess_energy_max_runtime_1",
        "sensor.keba_keenergy_12345678_external_heat_source_excess_energy_max_runtime_2",
        "sensor.keba_keenergy_12345678_external_heat_source_excess_energy_operating_time_1",
        "sensor.keba_keenergy_12345678_external_heat_source_excess_energy_operating_time_2",
        "sensor.keba_keenergy_12345678_external_heat_source_max_runtime_1",
        "sensor.keba_keenergy_12345678_external_heat_source_max_runtime_2",
        "sensor.keba_keenergy_12345678_external_heat_source_operating_mode_1",
        "sensor.keba_keenergy_12345678_external_heat_source_operating_mode_2",
        "sensor.keba_keenergy_12345678_external_heat_source_operating_time_1",
        "sensor.keba_keenergy_12345678_external_heat_source_operating_time_2",
        "sensor.keba_keenergy_12345678_external_heat_source_target_temperature_1",
        "sensor.keba_keenergy_12345678_external_heat_source_target_temperature_2",
        # switch valve
        "sensor.keba_keenergy_12345678_switch_valve_position_1",
        "sensor.keba_keenergy_12345678_switch_valve_position_2",
        # photovoltaics
        "sensor.keba_keenergy_12345678_photovoltaics_daily_energy",
        "sensor.keba_keenergy_12345678_photovoltaics_excess_power",
        "sensor.keba_keenergy_12345678_photovoltaics_total_energy",
    ],
)
@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensors(
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


@pytest.mark.parametrize(
    ("entity", "translation"),
    [
        # system
        ("sensor.keba_keenergy_12345678_operating_mode", "system_operating_mode"),
        # buffer tank
        ("sensor.keba_keenergy_12345678_buffer_tank_operating_mode_1", "buffer_tank_operating_mode"),
        ("sensor.keba_keenergy_12345678_buffer_tank_operating_mode_2", "buffer_tank_operating_mode"),
        # hot water tank
        ("sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_1", "hot_water_tank_operating_mode"),
        ("sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_2", "hot_water_tank_operating_mode"),
        # heat pump
        ("sensor.keba_keenergy_12345678_heat_pump_state", "state"),
        ("sensor.keba_keenergy_12345678_heat_pump_substate", "substate"),
        # heating circuit
        ("sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1", "heat_circuit_operating_mode"),
        ("sensor.keba_keenergy_12345678_heat_circuit_operating_mode_2", "heat_circuit_operating_mode"),
        ("sensor.keba_keenergy_12345678_heat_circuit_heat_request_1", "heat_request"),
        # external heat source
        ("sensor.keba_keenergy_12345678_external_heat_source_operating_mode_1", "external_heat_source_operating_mode"),
        # switch valve
        ("sensor.keba_keenergy_12345678_switch_valve_position_1", "switch_valve_position"),
        ("sensor.keba_keenergy_12345678_switch_valve_position_2", "switch_valve_position"),
    ],
)
@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensors_options_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    language: str,
    entity: str,
    translation: str,
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
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    _entity: State | None = hass.states.get(entity)
    assert isinstance(_entity, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.{translation}.state.{opt}"]
        for opt in _entity.attributes[ATTR_OPTIONS]
    } == snapshot
