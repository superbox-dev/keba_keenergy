import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_SSL
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests.conftest import FakeKebaKeEnergyAPI


async def test_load_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test initial load."""
    fake_api.register_requests(config_entry.data[CONF_HOST])
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED

    assert hass.states.async_entity_ids_count() == 26

    assert set(hass.states.async_entity_ids()) == {
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_heat_request",
        "binary_sensor.keba_keenergy_12345678_heat_pump_heat_request",
        "climate.keba_keenergy_12345678",
        "water_heater.keba_keenergy_12345678",
        "sensor.keba_keenergy_12345678_outdoor_temperature",
        "sensor.keba_keenergy_12345678_hot_water_tank_temperature",
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode",
        "sensor.keba_keenergy_12345678_hot_water_tank_min_temperature",
        "sensor.keba_keenergy_12345678_hot_water_tank_max_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_state",
        "sensor.keba_keenergy_12345678_heat_pump_inflow_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_reflux_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_source_input_temperature",
        "sensor.keba_keenergy_12345678_heat_pump_source_output_temperature",
        "sensor.keba_keenergy_12345678_heat_circuit_temperature",
        "sensor.keba_keenergy_12345678_heat_circuit_day_temperature",
        "sensor.keba_keenergy_12345678_heat_circuit_night_temperature",
        "sensor.keba_keenergy_12345678_heat_circuit_holiday_temperature",
        "sensor.keba_keenergy_12345678_heat_circuit_temperature_offset",
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode",
        "sensor.keba_keenergy_12345678_heat_circuit_heat_request",
        "number.keba_keenergy_12345678_hot_water_tank_min_temperature",
        "number.keba_keenergy_12345678_hot_water_tank_max_temperature",
        "number.keba_keenergy_12345678_heat_circuit_day_temperature",
        "number.keba_keenergy_12345678_heat_circuit_night_temperature",
        "number.keba_keenergy_12345678_heat_circuit_holiday_temperature",
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
    fake_api.register_requests(config_entry.data[CONF_HOST])
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED
