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
from homeassistant.const import STATE_ON
from homeassistant.const import STATE_STANDBY
from homeassistant.const import UnitOfEnergy
from homeassistant.const import UnitOfPower
from homeassistant.const import UnitOfPressure
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test sensors."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    outdoor_temperature: State | None = hass.states.get("sensor.keba_keenergy_12345678_outdoor_temperature")
    assert isinstance(outdoor_temperature, State)
    assert outdoor_temperature.state == "20.5"
    assert outdoor_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert outdoor_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert outdoor_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert outdoor_temperature.attributes[ATTR_FRIENDLY_NAME] == "KEBA KeEnergy Outdoor temperature"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_hot_water_tank_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test hot water tank sensors."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    hot_water_tank_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_temperature_1",
    )
    assert isinstance(hot_water_tank_temperature_1, State)
    assert hot_water_tank_temperature_1.state == "47.7"
    assert hot_water_tank_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert hot_water_tank_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank (1) Temperature"

    hot_water_tank_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_1",
    )
    assert isinstance(hot_water_tank_operating_mode_1, State)
    assert hot_water_tank_operating_mode_1.state == "heat_up"
    assert hot_water_tank_operating_mode_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert hot_water_tank_operating_mode_1.attributes[ATTR_OPTIONS] == ["auto", "heat_up", "off", "on"]
    assert hot_water_tank_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank (1) Operating mode"

    hot_water_tank_min_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_min_temperature_1",
    )
    assert isinstance(hot_water_tank_min_temperature_1, State)
    assert hot_water_tank_min_temperature_1.state == "32.5"
    assert hot_water_tank_min_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_min_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert hot_water_tank_min_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_min_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank (1) Minimum temperature"

    hot_water_tank_max_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_max_temperature_1",
    )
    assert isinstance(hot_water_tank_max_temperature_1, State)
    assert hot_water_tank_max_temperature_1.state == "51.0"
    assert hot_water_tank_max_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_max_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert hot_water_tank_max_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_max_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank (1) Maximum temperature"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_hot_water_tank_sensors_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test hot water tank sensors translations."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    hot_water_tank_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_temperature_1",
    )
    assert isinstance(hot_water_tank_temperature_1, State)
    assert hot_water_tank_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher (1) Temperatur"

    hot_water_tank_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_1",
    )
    assert isinstance(hot_water_tank_operating_mode_1, State)
    assert hot_water_tank_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher (1) Betriebsart"

    hot_water_tank_min_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_min_temperature_1",
    )
    assert isinstance(hot_water_tank_min_temperature_1, State)
    assert (
        hot_water_tank_min_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher (1) Minimale Temperatur"
    )

    hot_water_tank_max_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_max_temperature_1",
    )
    assert isinstance(hot_water_tank_max_temperature_1, State)
    assert (
        hot_water_tank_max_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher (1) Maximale Temperatur"
    )


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_pump_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test sensors."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    heat_pump_state: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_state")
    assert isinstance(heat_pump_state, State)
    assert heat_pump_state.state == STATE_STANDBY
    assert heat_pump_state.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_pump_state.attributes[ATTR_OPTIONS] == [
        "standby",
        "flow",
        "auto_heat",
        "defrost",
        "auto_cool",
        "inflow",
    ]
    assert heat_pump_state.attributes[ATTR_FRIENDLY_NAME] == "Heat pump State"

    heat_pump_circulation_pump: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_circulation_pump",
    )
    assert isinstance(heat_pump_circulation_pump, State)
    assert heat_pump_circulation_pump.state == "0.0"
    assert heat_pump_circulation_pump.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert heat_pump_circulation_pump.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_circulation_pump.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Circulation pump"

    heat_pump_inflow_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_inflow_temperature",
    )
    assert isinstance(heat_pump_inflow_temperature, State)
    assert heat_pump_inflow_temperature.state == "24.8"
    assert heat_pump_inflow_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_inflow_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_inflow_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_inflow_temperature.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Inflow temperature"

    heat_pump_reflux_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_reflux_temperature",
    )
    assert isinstance(heat_pump_reflux_temperature, State)
    assert heat_pump_reflux_temperature.state == "23.9"
    assert heat_pump_reflux_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_reflux_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_reflux_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_reflux_temperature.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Reflux temperature"

    heat_pump_source_input_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_source_input_temperature",
    )
    assert isinstance(heat_pump_source_input_temperature, State)
    assert heat_pump_source_input_temperature.state == "25.7"
    assert heat_pump_source_input_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_source_input_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_source_input_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_source_input_temperature.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Source input temperature"

    heat_pump_source_output_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_source_output_temperature",
    )
    assert isinstance(heat_pump_source_output_temperature, State)
    assert heat_pump_source_output_temperature.state == "24.9"
    assert heat_pump_source_output_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_source_output_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_source_output_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_source_output_temperature.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Source output temperature"

    heat_pump_compressor_input_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_compressor_input_temperature",
    )
    assert isinstance(heat_pump_compressor_input_temperature, State)
    assert heat_pump_compressor_input_temperature.state == "27.2"
    assert heat_pump_compressor_input_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_compressor_input_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_compressor_input_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_pump_compressor_input_temperature.attributes[ATTR_FRIENDLY_NAME]
        == "Heat pump Compressor input temperature"
    )

    heat_pump_compressor_output_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_compressor_output_temperature",
    )
    assert isinstance(heat_pump_compressor_output_temperature, State)
    assert heat_pump_compressor_output_temperature.state == "27.2"
    assert heat_pump_compressor_output_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_compressor_output_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_compressor_output_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_pump_compressor_output_temperature.attributes[ATTR_FRIENDLY_NAME]
        == "Heat pump Compressor output temperature"
    )

    heat_pump_compressor: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_compressor")
    assert isinstance(heat_pump_compressor, State)
    assert heat_pump_compressor.state == "0.0"
    assert heat_pump_compressor.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert heat_pump_compressor.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_compressor.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Compressor"

    heat_pump_high_pressure: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_high_pressure")
    assert isinstance(heat_pump_high_pressure, State)
    assert heat_pump_high_pressure.state == "15.62"
    assert heat_pump_high_pressure.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPressure.BAR
    assert heat_pump_high_pressure.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_high_pressure.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.PRESSURE
    assert heat_pump_high_pressure.attributes[ATTR_FRIENDLY_NAME] == "Heat pump High pressure"

    heat_pump_low_pressure: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_low_pressure")
    assert isinstance(heat_pump_low_pressure, State)
    assert heat_pump_low_pressure.state == "15.35"
    assert heat_pump_low_pressure.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPressure.BAR
    assert heat_pump_low_pressure.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_low_pressure.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.PRESSURE
    assert heat_pump_low_pressure.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Low pressure"

    heat_pump_electrical_power: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_electrical_power",
    )
    assert isinstance(heat_pump_electrical_power, State)
    assert heat_pump_electrical_power.state == "5.52"
    assert heat_pump_electrical_power.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPower.KILO_WATT
    assert heat_pump_electrical_power.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_electrical_power.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.POWER
    assert heat_pump_electrical_power.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Electrical power"

    heat_pump_heating_power: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_power")
    assert isinstance(heat_pump_heating_power, State)
    assert heat_pump_heating_power.state == "3.22"
    assert heat_pump_heating_power.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPower.KILO_WATT
    assert heat_pump_heating_power.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_heating_power.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.POWER
    assert heat_pump_heating_power.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heating power"

    heat_pump_hot_water_power: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_hot_water_power")
    assert isinstance(heat_pump_hot_water_power, State)
    assert heat_pump_hot_water_power.state == "2.77"
    assert heat_pump_hot_water_power.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPower.KILO_WATT
    assert heat_pump_hot_water_power.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_hot_water_power.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.POWER
    assert heat_pump_hot_water_power.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Hot water power"

    heat_pump_cop: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cop")
    assert isinstance(heat_pump_cop, State)
    assert heat_pump_cop.state == "2.55"
    assert heat_pump_cop.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_cop.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Coefficient of performance"

    heat_pump_heating_energy: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_energy")
    assert isinstance(heat_pump_heating_energy, State)
    assert heat_pump_heating_energy.state == "8.43"
    assert heat_pump_heating_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_heating_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert heat_pump_heating_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_heating_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heating energy"

    heat_pump_heating_electrical_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_heating_electrical_energy",
    )
    assert isinstance(heat_pump_heating_electrical_energy, State)
    assert heat_pump_heating_electrical_energy.state == "7.33"
    assert heat_pump_heating_electrical_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_heating_electrical_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert heat_pump_heating_electrical_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_heating_electrical_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heating electrical energy"

    heat_pump_heating_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_spf")
    assert isinstance(heat_pump_heating_spf, State)
    assert heat_pump_heating_spf.state == "3.32"
    assert heat_pump_heating_spf.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_heating_spf.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heating SPF"

    heat_pump_cooling_energy: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cooling_energy")
    assert isinstance(heat_pump_cooling_energy, State)
    assert heat_pump_cooling_energy.state == "7.21"
    assert heat_pump_cooling_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_cooling_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert heat_pump_cooling_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_cooling_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Cooling energy"

    heat_pump_cooling_electrical_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_cooling_electrical_energy",
    )
    assert isinstance(heat_pump_cooling_electrical_energy, State)
    assert heat_pump_cooling_electrical_energy.state == "8.72"
    assert heat_pump_cooling_electrical_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_cooling_electrical_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert heat_pump_cooling_electrical_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_cooling_electrical_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Cooling electrical energy"

    heat_pump_cooling_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cooling_spf")
    assert isinstance(heat_pump_cooling_spf, State)
    assert heat_pump_cooling_spf.state == "4.22"
    assert heat_pump_cooling_spf.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_cooling_spf.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Cooling SPF"

    heat_pump_domestic_hot_water_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_domestic_hot_water_energy",
    )
    assert isinstance(heat_pump_domestic_hot_water_energy, State)
    assert heat_pump_domestic_hot_water_energy.state == "7.86"
    assert heat_pump_domestic_hot_water_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_domestic_hot_water_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert heat_pump_domestic_hot_water_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_domestic_hot_water_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Hot water energy"

    heat_pump_domestic_hot_water_electrical_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_domestic_hot_water_electrical_energy",
    )
    assert isinstance(heat_pump_domestic_hot_water_electrical_energy, State)
    assert heat_pump_domestic_hot_water_electrical_energy.state == "2.77"
    assert (
        heat_pump_domestic_hot_water_electrical_energy.attributes[CONF_UNIT_OF_MEASUREMENT]
        == UnitOfEnergy.KILO_WATT_HOUR
    )
    assert (
        heat_pump_domestic_hot_water_electrical_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    )
    assert heat_pump_domestic_hot_water_electrical_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert (
        heat_pump_domestic_hot_water_electrical_energy.attributes[ATTR_FRIENDLY_NAME]
        == "Heat pump Hot water electrical energy"
    )

    heat_pump_domestic_hot_water_spf: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_domestic_hot_water_spf",
    )
    assert isinstance(heat_pump_domestic_hot_water_spf, State)
    assert heat_pump_domestic_hot_water_spf.state == "2.5"
    assert heat_pump_domestic_hot_water_spf.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_domestic_hot_water_spf.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Hot water SPF"

    heat_pump_total_energy: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_total_energy")
    assert isinstance(heat_pump_total_energy, State)
    assert heat_pump_total_energy.state == "8.22"
    assert heat_pump_total_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_total_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert heat_pump_total_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_total_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Total energy"

    heat_pump_total_electrical_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_total_electrical_energy",
    )
    assert isinstance(heat_pump_total_electrical_energy, State)
    assert heat_pump_total_electrical_energy.state == "5.21"
    assert heat_pump_total_electrical_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_total_electrical_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert heat_pump_total_electrical_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_total_electrical_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Total electrical energy"

    heat_pump_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_spf")
    assert isinstance(heat_pump_spf, State)
    assert heat_pump_spf.state == "2.43"
    assert heat_pump_spf.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_spf.attributes[ATTR_FRIENDLY_NAME] == "Heat pump SPF"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_pump_sensors_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test heat pump sensors translations."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    heat_pump_state: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_state")
    assert isinstance(heat_pump_state, State)
    assert heat_pump_state.attributes[ATTR_OPTIONS] == [
        "standby",
        "flow",
        "auto_heat",
        "defrost",
        "auto_cool",
        "inflow",
    ]
    assert heat_pump_state.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Status"

    heat_pump_circulation_pump: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_circulation_pump",
    )
    assert isinstance(heat_pump_circulation_pump, State)
    assert heat_pump_circulation_pump.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Umwälzpumpe"

    heat_pump_inflow_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_inflow_temperature",
    )
    assert isinstance(heat_pump_inflow_temperature, State)
    assert heat_pump_inflow_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Vorlauftemperatur"

    heat_pump_reflux_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_reflux_temperature",
    )
    assert isinstance(heat_pump_reflux_temperature, State)
    assert heat_pump_reflux_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Rücklauftemperatur"

    heat_pump_source_input_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_source_input_temperature",
    )
    assert isinstance(heat_pump_source_input_temperature, State)
    assert heat_pump_source_input_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Temperatur Quelle Eingang"

    heat_pump_source_output_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_source_output_temperature",
    )
    assert isinstance(heat_pump_source_output_temperature, State)
    assert heat_pump_source_output_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Temperatur Quelle Ausgang"

    heat_pump_compressor_input_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_compressor_input_temperature",
    )
    assert isinstance(heat_pump_compressor_input_temperature, State)
    assert (
        heat_pump_compressor_input_temperature.attributes[ATTR_FRIENDLY_NAME]
        == "Wärmepumpe Kompressor Eingangstemperatur"
    )

    heat_pump_compressor_output_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_compressor_output_temperature",
    )
    assert isinstance(heat_pump_compressor_output_temperature, State)
    assert (
        heat_pump_compressor_output_temperature.attributes[ATTR_FRIENDLY_NAME]
        == "Wärmepumpe Kompressor Ausgangstemperatur"
    )

    heat_pump_compressor: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_compressor")
    assert isinstance(heat_pump_compressor, State)
    assert heat_pump_compressor.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Kompressor"

    heat_pump_high_pressure: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_high_pressure")
    assert isinstance(heat_pump_high_pressure, State)
    assert heat_pump_high_pressure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Hochdruck"

    heat_pump_low_pressure: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_low_pressure")
    assert isinstance(heat_pump_low_pressure, State)
    assert heat_pump_low_pressure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Niederdruck"

    heat_pump_electrical_power: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_electrical_power",
    )
    assert isinstance(heat_pump_electrical_power, State)
    assert heat_pump_electrical_power.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Elektrische Leistung"

    heat_pump_heating_power: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_power")
    assert isinstance(heat_pump_heating_power, State)
    assert heat_pump_heating_power.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Heizleistung"

    heat_pump_hot_water_power: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_hot_water_power")
    assert isinstance(heat_pump_hot_water_power, State)
    assert heat_pump_hot_water_power.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Warmwasserleistung"

    heat_pump_cop: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cop")
    assert isinstance(heat_pump_cop, State)
    assert heat_pump_cop.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Leistungszahl"

    heat_pump_heating_energy: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_energy")
    assert isinstance(heat_pump_heating_energy, State)
    assert heat_pump_heating_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Wärmemenge"

    heat_pump_heating_electrical_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_heating_electrical_energy",
    )
    assert isinstance(heat_pump_heating_electrical_energy, State)
    assert heat_pump_heating_electrical_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Elektrische Heizenergie"

    heat_pump_heating_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_spf")
    assert isinstance(heat_pump_heating_spf, State)
    assert heat_pump_heating_spf.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe JAZ Heizen"

    heat_pump_cooling_energy: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cooling_energy")
    assert isinstance(heat_pump_cooling_energy, State)
    assert heat_pump_cooling_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Kühlmenge"

    heat_pump_cooling_electrical_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_cooling_electrical_energy",
    )
    assert isinstance(heat_pump_cooling_electrical_energy, State)
    assert heat_pump_cooling_electrical_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Elektrische Kühlenergie"

    heat_pump_cooling_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cooling_spf")
    assert isinstance(heat_pump_cooling_spf, State)
    assert heat_pump_cooling_spf.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe JAZ Kühlen"

    heat_pump_domestic_hot_water_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_domestic_hot_water_energy",
    )
    assert isinstance(heat_pump_domestic_hot_water_energy, State)
    assert heat_pump_domestic_hot_water_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Warmwasserenergie"

    heat_pump_domestic_hot_water_electrical_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_domestic_hot_water_electrical_energy",
    )
    assert isinstance(heat_pump_domestic_hot_water_electrical_energy, State)
    assert (
        heat_pump_domestic_hot_water_electrical_energy.attributes[ATTR_FRIENDLY_NAME]
        == "Wärmepumpe Elektrische Warmwasserenergie"
    )

    heat_pump_domestic_hot_water_spf: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_domestic_hot_water_spf",
    )
    assert isinstance(heat_pump_domestic_hot_water_spf, State)
    assert heat_pump_domestic_hot_water_spf.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe JAZ Warmwasser"

    heat_pump_total_energy: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_total_energy")
    assert isinstance(heat_pump_total_energy, State)
    assert heat_pump_total_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Gesamte Energie"

    heat_pump_total_electrical_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_total_electrical_energy",
    )
    assert isinstance(heat_pump_total_electrical_energy, State)
    assert heat_pump_total_electrical_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Gesamte elektrische Energie"

    heat_pump_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_spf")
    assert isinstance(heat_pump_spf, State)
    assert heat_pump_spf.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe JAZ"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_circuit_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test heat circuit sensors."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    heat_circuit_room_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_1",
    )
    assert isinstance(heat_circuit_room_temperature_1, State)
    assert heat_circuit_room_temperature_1.state == "22.42"
    assert heat_circuit_room_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_room_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_room_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_room_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit (1) Room temperature"

    heat_circuit_room_humidity_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_room_humidity_1",
    )
    assert isinstance(heat_circuit_room_humidity_1, State)
    assert heat_circuit_room_humidity_1.state == "53.0"
    assert heat_circuit_room_humidity_1.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert heat_circuit_room_humidity_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_room_humidity_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.HUMIDITY
    assert heat_circuit_room_humidity_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit (1) Room humidity"

    heat_circuit_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_temperature_1",
    )
    assert isinstance(heat_circuit_temperature_1, State)
    assert heat_circuit_temperature_1.state == "20.5"
    assert heat_circuit_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit (1) Temperature"

    heat_circuit_day_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_day_temperature_1",
    )
    assert isinstance(heat_circuit_day_temperature_1, State)
    assert heat_circuit_day_temperature_1.state == "20.5"
    assert heat_circuit_day_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_day_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_day_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_day_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit (1) Day temperature"

    heat_circuit_day_temperature_threshold_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_day_temperature_threshold_1",
    )
    assert isinstance(heat_circuit_day_temperature_threshold_1, State)
    assert heat_circuit_day_temperature_threshold_1.state == "20.0"
    assert heat_circuit_day_temperature_threshold_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_day_temperature_threshold_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_day_temperature_threshold_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_day_temperature_threshold_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit (1) Day temperature threshold"
    )

    heat_circuit_night_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_night_temperature_1",
    )
    assert isinstance(heat_circuit_night_temperature_1, State)
    assert heat_circuit_night_temperature_1.state == "20.0"
    assert heat_circuit_night_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_night_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_night_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_night_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit (1) Night temperature"

    heat_circuit_night_temperature_threshold_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_night_temperature_threshold_1",
    )
    assert isinstance(heat_circuit_night_temperature_threshold_1, State)
    assert heat_circuit_night_temperature_threshold_1.state == "18.0"
    assert heat_circuit_night_temperature_threshold_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_night_temperature_threshold_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_night_temperature_threshold_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_night_temperature_threshold_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit (1) Night temperature threshold"
    )

    heat_circuit_holiday_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_holiday_temperature_1",
    )
    assert isinstance(heat_circuit_holiday_temperature_1, State)
    assert heat_circuit_holiday_temperature_1.state == "18.0"
    assert heat_circuit_holiday_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_holiday_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_holiday_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_holiday_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit (1) Holiday temperature"
    )

    heat_circuit_temperature_offset_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_temperature_offset_1",
    )
    assert isinstance(heat_circuit_temperature_offset_1, State)
    assert heat_circuit_temperature_offset_1.state == "1.5"
    assert heat_circuit_temperature_offset_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_temperature_offset_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_temperature_offset_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_temperature_offset_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit (1) Temperature offset"

    heat_circuit_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1",
    )
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.state == "day"
    assert heat_circuit_operating_mode_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_circuit_operating_mode_1.attributes[ATTR_OPTIONS] == ["off", "auto", "day", "night", "holiday", "party"]
    assert heat_circuit_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit (1) Operating mode"

    heat_circuit_heat_request_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heat_request_1",
    )
    assert isinstance(heat_circuit_heat_request_1, State)
    assert heat_circuit_heat_request_1.state == STATE_ON
    assert heat_circuit_heat_request_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_circuit_heat_request_1.attributes[ATTR_OPTIONS] == [
        "off",
        "on",
        "temporary_off",
        "outdoor_temperature_off",
    ]
    assert heat_circuit_heat_request_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit (1) Heat request"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_circuit_sensors_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test heat circuit sensors translations."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    heat_circuit_room_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_1",
    )
    assert isinstance(heat_circuit_room_temperature_1, State)
    assert heat_circuit_room_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Raumtemperatur"

    heat_circuit_room_humidity_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_room_humidity_1",
    )
    assert isinstance(heat_circuit_room_humidity_1, State)
    assert heat_circuit_room_humidity_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Raumluftfeuchtigkeit"

    heat_circuit_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_temperature_1",
    )
    assert isinstance(heat_circuit_temperature_1, State)
    assert heat_circuit_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Temperatur"

    heat_circuit_day_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_day_temperature_1",
    )
    assert isinstance(heat_circuit_day_temperature_1, State)
    assert heat_circuit_day_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Temperatur Tag"

    heat_circuit_day_temperature_threshold_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_day_temperature_threshold_1",
    )
    assert isinstance(heat_circuit_day_temperature_threshold_1, State)
    assert heat_circuit_day_temperature_threshold_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Heizgrenze Tag"

    heat_circuit_night_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_night_temperature_1",
    )
    assert isinstance(heat_circuit_night_temperature_1, State)
    assert heat_circuit_night_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Temperatur Nacht"

    heat_circuit_night_temperature_threshold_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_night_temperature_threshold_1",
    )
    assert isinstance(heat_circuit_night_temperature_threshold_1, State)
    assert heat_circuit_night_temperature_threshold_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Heizgrenze Nacht"

    heat_circuit_holiday_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_holiday_temperature_1",
    )
    assert isinstance(heat_circuit_holiday_temperature_1, State)
    assert heat_circuit_holiday_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Temperature Urlaub"

    heat_circuit_temperature_offset_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_temperature_offset_1",
    )
    assert isinstance(heat_circuit_temperature_offset_1, State)
    assert heat_circuit_temperature_offset_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Temperatur Offset"

    heat_circuit_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1",
    )
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis (1) Betriebsart"

    heat_circuit_heat_request_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heat_request_1",
    )
    assert isinstance(heat_circuit_heat_request_1, State)
    assert heat_circuit_heat_request_1.attributes[ATTR_OPTIONS] == [
        "off",
        "on",
        "temporary_off",
        "outdoor_temperature_off",
    ]
    assert heat_circuit_heat_request_1.attributes.get(ATTR_FRIENDLY_NAME) == "Heizkreis (1) Heizanforderung"
