import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_SSL
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multi_positions_data_response
from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_load_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test initial load."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    assert config_entry.state is ConfigEntryState.LOADED
    assert hass.states.async_entity_ids_count() == 169

    assert set(hass.states.async_entity_ids()) == {
        "binary_sensor.keba_keenergy_12345678_buffer_tank_cool_request_1",
        "binary_sensor.keba_keenergy_12345678_buffer_tank_cool_request_2",
        "binary_sensor.keba_keenergy_12345678_buffer_tank_heat_request_1",
        "binary_sensor.keba_keenergy_12345678_buffer_tank_heat_request_2",
        "binary_sensor.keba_keenergy_12345678_external_heat_source_heat_request_1",
        "binary_sensor.keba_keenergy_12345678_external_heat_source_heat_request_2",
        "binary_sensor.keba_keenergy_12345678_heat_pump_heat_request",
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_heat_request_1",
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_heat_request_2",
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_hot_water_flow_1",
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_hot_water_flow_2",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_1",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_2",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_1",
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_2",
        "climate.keba_keenergy_12345678_1",
        "climate.keba_keenergy_12345678_2",
        "select.keba_keenergy_12345678_buffer_tank_operating_mode_1",
        "select.keba_keenergy_12345678_buffer_tank_operating_mode_2",
        "select.keba_keenergy_12345678_external_heat_source_operating_mode_1",
        "select.keba_keenergy_12345678_external_heat_source_operating_mode_2",
        "select.keba_keenergy_12345678_operating_mode",
        "select.keba_keenergy_12345678_heat_circuit_operating_mode_1",
        "select.keba_keenergy_12345678_heat_circuit_operating_mode_2",
        "select.keba_keenergy_12345678_hot_water_tank_operating_mode_1",
        "select.keba_keenergy_12345678_hot_water_tank_operating_mode_2",
        "select.keba_keenergy_12345678_solar_circuit_operating_mode_1",
        "select.keba_keenergy_12345678_solar_circuit_operating_mode_2",
        "number.keba_keenergy_12345678_buffer_tank_standby_temperature_1",
        "number.keba_keenergy_12345678_buffer_tank_standby_temperature_2",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_away_1",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_away_2",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_2",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_night_1",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_night_2",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_offset_2",
        "number.keba_keenergy_12345678_hot_water_tank_standby_temperature_1",
        "number.keba_keenergy_12345678_hot_water_tank_standby_temperature_2",
        "number.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
        "number.keba_keenergy_12345678_hot_water_tank_target_temperature_2",
        "number.keba_keenergy_12345678_solar_circuit_target_temperature_1_1",
        "number.keba_keenergy_12345678_solar_circuit_target_temperature_1_2",
        "number.keba_keenergy_12345678_solar_circuit_target_temperature_2_1",
        "number.keba_keenergy_12345678_solar_circuit_target_temperature_2_2",
        "sensor.keba_keenergy_12345678_buffer_tank_current_bottom_temperature_1",
        "sensor.keba_keenergy_12345678_buffer_tank_current_bottom_temperature_2",
        "sensor.keba_keenergy_12345678_buffer_tank_current_top_temperature_1",
        "sensor.keba_keenergy_12345678_buffer_tank_current_top_temperature_2",
        "sensor.keba_keenergy_12345678_buffer_tank_operating_mode_1",
        "sensor.keba_keenergy_12345678_buffer_tank_operating_mode_2",
        "sensor.keba_keenergy_12345678_buffer_tank_standby_temperature_1",
        "sensor.keba_keenergy_12345678_buffer_tank_standby_temperature_2",
        "sensor.keba_keenergy_12345678_buffer_tank_target_temperature_1",
        "sensor.keba_keenergy_12345678_buffer_tank_target_temperature_2",
        "sensor.keba_keenergy_12345678_control_cpu_usage",
        "sensor.keba_keenergy_12345678_cpu_usage",
        "sensor.keba_keenergy_12345678_external_heat_source_operating_mode_1",
        "sensor.keba_keenergy_12345678_external_heat_source_operating_mode_2",
        "sensor.keba_keenergy_12345678_external_heat_source_target_temperature_1",
        "sensor.keba_keenergy_12345678_external_heat_source_target_temperature_2",
        "sensor.keba_keenergy_12345678_external_heat_source_operating_time_1",
        "sensor.keba_keenergy_12345678_external_heat_source_operating_time_2",
        "sensor.keba_keenergy_12345678_external_heat_source_max_runtime_1",
        "sensor.keba_keenergy_12345678_external_heat_source_max_runtime_2",
        "sensor.keba_keenergy_12345678_external_heat_source_activation_counter_1",
        "sensor.keba_keenergy_12345678_external_heat_source_activation_counter_2",
        "sensor.keba_keenergy_12345678_free_ram",
        "sensor.keba_keenergy_12345678_heat_circuit_dew_point_1",
        "sensor.keba_keenergy_12345678_heat_circuit_dew_point_2",
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_2",
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_setpoint_1",
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_setpoint_2",
        "sensor.keba_keenergy_12345678_heat_circuit_heat_request_1",
        "sensor.keba_keenergy_12345678_heat_circuit_heat_request_2",
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_day_1",
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_day_2",
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_night_1",
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_night_2",
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1",
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_2",
        "sensor.keba_keenergy_12345678_heat_circuit_return_flow_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_return_flow_temperature_2",
        "sensor.keba_keenergy_12345678_heat_circuit_room_humidity_1",
        "sensor.keba_keenergy_12345678_heat_circuit_room_humidity_2",
        "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_2",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_2",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_away_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_away_2",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_day_2",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_night_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_night_2",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1",
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_offset_2",
        "sensor.keba_keenergy_12345678_heat_pump_circulation_pump",
        "sensor.keba_keenergy_12345678_heat_pump_compressor",
        "sensor.keba_keenergy_12345678_heat_pump_compressor_input_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_compressor_output_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_compressor_power",
        "sensor.keba_keenergy_12345678_heat_pump_cooling_energy",
        "sensor.keba_keenergy_12345678_heat_pump_cooling_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_cooling_spf",
        "sensor.keba_keenergy_12345678_heat_pump_cop",
        "sensor.keba_keenergy_12345678_heat_pump_flow_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_heating_energy",
        "sensor.keba_keenergy_12345678_heat_pump_heating_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_heating_power",
        "sensor.keba_keenergy_12345678_heat_pump_heating_spf",
        "sensor.keba_keenergy_12345678_heat_pump_high_pressure",
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_energy",
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_power",
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_spf",
        "sensor.keba_keenergy_12345678_heat_pump_low_pressure",
        "sensor.keba_keenergy_12345678_heat_pump_return_flow_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_source_input_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_source_output_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_state",
        "sensor.keba_keenergy_12345678_heat_pump_sub_state",
        "sensor.keba_keenergy_12345678_heat_pump_total_energy_consumption",
        "sensor.keba_keenergy_12345678_heat_pump_total_spf",
        "sensor.keba_keenergy_12345678_heat_pump_total_thermal_energy",
        "sensor.keba_keenergy_12345678_heat_pump_operating_time",
        "sensor.keba_keenergy_12345678_heat_pump_max_runtime",
        "sensor.keba_keenergy_12345678_heat_pump_activation_counter",
        "sensor.keba_keenergy_12345678_hot_water_tank_current_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_current_temperature_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_standby_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_standby_temperature_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_target_temperature_2",
        "sensor.keba_keenergy_12345678_hot_water_tank_fresh_water_module_temperature_1",
        "sensor.keba_keenergy_12345678_hot_water_tank_fresh_water_module_temperature_2",
        "sensor.keba_keenergy_12345678_operating_mode",
        "sensor.keba_keenergy_12345678_outdoor_temperature",
        # "sensor.keba_keenergy_12345678_photovoltaic_excess_power",
        # "sensor.keba_keenergy_12345678_photovoltaic_daily_energy",
        # "sensor.keba_keenergy_12345678_photovoltaic_total_energy",
        "sensor.keba_keenergy_12345678_ram_usage",
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
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_1_1",
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_1_2",
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_2_1",
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_2_2",
        "sensor.keba_keenergy_12345678_solar_circuit_source_temperature_1",
        "sensor.keba_keenergy_12345678_solar_circuit_source_temperature_2",
        "sensor.keba_keenergy_12345678_webserver_cpu_usage",
        "sensor.keba_keenergy_12345678_webview_cpu_usage",
        "water_heater.keba_keenergy_12345678_1",
        "water_heater.keba_keenergy_12345678_2",
        "water_heater.keba_keenergy_12345678_buffer_tank_1",
        "water_heater.keba_keenergy_12345678_buffer_tank_2",
    }


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
    """Test unload."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    assert config_entry.state == ConfigEntryState.LOADED
    await hass.config_entries.async_unload(config_entry.entry_id)
    assert config_entry.state == ConfigEntryState.NOT_LOADED
