import pytest
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorStateClass
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.components.sensor.const import ATTR_STATE_CLASS
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.const import CONF_DEVICE_CLASS
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT
from homeassistant.const import PERCENTAGE
from homeassistant.const import UnitOfPressure
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test binary sensors."""
    fake_api.register_requests(config_entry.data[CONF_HOST])
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    outdoor_temperature: State | None = hass.states.get("sensor.keba_keenergy_12345678_outdoor_temperature")
    assert isinstance(outdoor_temperature, State)
    assert outdoor_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert outdoor_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert outdoor_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert outdoor_temperature.attributes[ATTR_FRIENDLY_NAME] == "KEBA KeEnergy Outdoor temperature"

    hot_water_tank_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_temperature_1",
    )
    assert isinstance(hot_water_tank_temperature_1, State)
    assert hot_water_tank_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert hot_water_tank_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot Water Tank (1) Temperature"

    hot_water_tank_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_1",
    )
    assert isinstance(hot_water_tank_operating_mode_1, State)
    assert hot_water_tank_operating_mode_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert hot_water_tank_operating_mode_1.attributes[ATTR_OPTIONS] == ["auto", "heat_up", "off", "on"]
    assert hot_water_tank_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Hot Water Tank (1) Operating mode"

    hot_water_tank_min_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_min_temperature_1",
    )
    assert isinstance(hot_water_tank_min_temperature_1, State)
    assert hot_water_tank_min_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_min_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert hot_water_tank_min_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_min_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot Water Tank (1) Minimum temperature"

    hot_water_tank_max_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_max_temperature_1",
    )
    assert isinstance(hot_water_tank_max_temperature_1, State)
    assert hot_water_tank_max_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_max_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert hot_water_tank_max_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_max_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot Water Tank (1) Maximum temperature"

    heat_pump_state: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_state")
    assert isinstance(heat_pump_state, State)
    assert heat_pump_state.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_pump_state.attributes[ATTR_OPTIONS] == [
        "standby",
        "flow",
        "auto_heat",
        "defrost",
        "auto_cool",
        "inflow",
    ]
    assert heat_pump_state.attributes[ATTR_FRIENDLY_NAME] == "M-TEC WPS26 State"

    heat_pump_circulation_pump: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_circulation_pump",
    )
    assert isinstance(heat_pump_circulation_pump, State)
    assert heat_pump_circulation_pump.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert heat_pump_circulation_pump.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_circulation_pump.attributes[ATTR_FRIENDLY_NAME] == "M-TEC WPS26 Circulation pump"

    heat_pump_inflow_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_inflow_temperature",
    )
    assert isinstance(heat_pump_inflow_temperature, State)
    assert heat_pump_inflow_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_inflow_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_inflow_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_inflow_temperature.attributes[ATTR_FRIENDLY_NAME] == "M-TEC WPS26 Inflow temperature"

    heat_pump_reflux_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_reflux_temperature",
    )
    assert isinstance(heat_pump_reflux_temperature, State)
    assert heat_pump_reflux_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_reflux_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_reflux_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_reflux_temperature.attributes[ATTR_FRIENDLY_NAME] == "M-TEC WPS26 Reflux temperature"

    heat_pump_source_input_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_source_input_temperature",
    )
    assert isinstance(heat_pump_source_input_temperature, State)
    assert heat_pump_source_input_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_source_input_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_source_input_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_source_input_temperature.attributes[ATTR_FRIENDLY_NAME] == "M-TEC WPS26 Source input temperature"

    heat_pump_source_output_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_source_output_temperature",
    )
    assert isinstance(heat_pump_source_output_temperature, State)
    assert heat_pump_source_output_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_source_output_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_source_output_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_source_output_temperature.attributes[ATTR_FRIENDLY_NAME] == "M-TEC WPS26 Source output temperature"

    heat_pump_compressor_input_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_compressor_input_temperature",
    )
    assert isinstance(heat_pump_compressor_input_temperature, State)
    assert heat_pump_compressor_input_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_compressor_input_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_compressor_input_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_pump_compressor_input_temperature.attributes[ATTR_FRIENDLY_NAME]
        == "M-TEC WPS26 Compressor input temperature"
    )

    heat_pump_compressor_output_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_compressor_output_temperature",
    )
    assert isinstance(heat_pump_compressor_output_temperature, State)
    assert heat_pump_compressor_output_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_compressor_output_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_compressor_output_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_pump_compressor_output_temperature.attributes[ATTR_FRIENDLY_NAME]
        == "M-TEC WPS26 Compressor output temperature"
    )

    heat_pump_compressor: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_compressor")
    assert isinstance(heat_pump_compressor, State)
    assert heat_pump_compressor.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert heat_pump_compressor.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_compressor.attributes[ATTR_FRIENDLY_NAME] == "M-TEC WPS26 Compressor"

    heat_pump_high_pressure: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_high_pressure")
    assert isinstance(heat_pump_high_pressure, State)
    assert heat_pump_high_pressure.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPressure.BAR
    assert heat_pump_high_pressure.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_high_pressure.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.PRESSURE
    assert heat_pump_high_pressure.attributes[ATTR_FRIENDLY_NAME] == "M-TEC WPS26 High pressure"

    heat_pump_low_pressure: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_low_pressure")
    assert isinstance(heat_pump_low_pressure, State)
    assert heat_pump_low_pressure.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPressure.BAR
    assert heat_pump_low_pressure.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_low_pressure.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.PRESSURE
    assert heat_pump_low_pressure.attributes[ATTR_FRIENDLY_NAME] == "M-TEC WPS26 Low pressure"

    heat_circuit_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_temperature_1",
    )
    assert isinstance(heat_circuit_temperature_1, State)
    assert heat_circuit_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "FBH1 (1) Temperature"

    heat_circuit_day_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_day_temperature_1",
    )
    assert isinstance(heat_circuit_day_temperature_1, State)
    assert heat_circuit_day_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_day_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_day_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_day_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "FBH1 (1) Day temperature"

    heat_circuit_day_temperature_threshold_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_day_temperature_threshold_1",
    )
    assert isinstance(heat_circuit_day_temperature_threshold_1, State)
    assert heat_circuit_day_temperature_threshold_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_day_temperature_threshold_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_day_temperature_threshold_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_day_temperature_threshold_1.attributes[ATTR_FRIENDLY_NAME] == "FBH1 (1) Day temperature threshold"
    )

    heat_circuit_night_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_night_temperature_1",
    )
    assert isinstance(heat_circuit_night_temperature_1, State)
    assert heat_circuit_night_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_night_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_night_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_night_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "FBH1 (1) Night temperature"

    heat_circuit_night_temperature_threshold_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_night_temperature_threshold_1",
    )
    assert isinstance(heat_circuit_night_temperature_threshold_1, State)
    assert heat_circuit_night_temperature_threshold_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_night_temperature_threshold_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_night_temperature_threshold_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_night_temperature_threshold_1.attributes[ATTR_FRIENDLY_NAME]
        == "FBH1 (1) Night temperature threshold"
    )

    heat_circuit_holiday_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_holiday_temperature_1",
    )
    assert isinstance(heat_circuit_holiday_temperature_1, State)
    assert heat_circuit_holiday_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_holiday_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_holiday_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_holiday_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "FBH1 (1) Holiday temperature"

    heat_circuit_temperature_offset_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_temperature_offset_1",
    )
    assert isinstance(heat_circuit_temperature_offset_1, State)
    assert heat_circuit_temperature_offset_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_temperature_offset_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_temperature_offset_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_temperature_offset_1.attributes[ATTR_FRIENDLY_NAME] == "FBH1 (1) Temperature offset"

    heat_circuit_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1",
    )
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_circuit_operating_mode_1.attributes[ATTR_OPTIONS] == ["off", "auto", "day", "night", "holiday", "party"]
    assert heat_circuit_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "FBH1 (1) Operating mode"

    heat_circuit_heat_request_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heat_request_1",
    )
    assert isinstance(heat_circuit_heat_request_1, State)
    assert heat_circuit_heat_request_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_circuit_heat_request_1.attributes[ATTR_OPTIONS] == [
        "off",
        "on",
        "temporary_off",
        "outdoor_temperature_off",
    ]
    assert heat_circuit_heat_request_1.attributes[ATTR_FRIENDLY_NAME] == "FBH1 (1) Heat request"
