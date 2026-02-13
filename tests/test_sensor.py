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
from homeassistant.const import UnitOfInformation
from homeassistant.const import UnitOfPower
from homeassistant.const import UnitOfPressure
from homeassistant.const import UnitOfTemperature
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import init_translations
from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_system_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    outdoor_temperature: State | None = hass.states.get("sensor.keba_keenergy_12345678_outdoor_temperature")
    assert isinstance(outdoor_temperature, State)
    assert outdoor_temperature.state == "20.5"
    assert outdoor_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert outdoor_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert outdoor_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert outdoor_temperature.attributes[ATTR_FRIENDLY_NAME] == "Control unit Outdoor temperature"

    operating_mode: State | None = hass.states.get("sensor.keba_keenergy_12345678_operating_mode")
    assert isinstance(operating_mode, State)
    assert operating_mode.state == "auto_heat"
    assert operating_mode.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert operating_mode.attributes[ATTR_OPTIONS] == ["setup", "standby", "summer", "auto_heat", "auto_cool", "auto"]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_system.state.{opt}"]
        for opt in operating_mode.attributes[ATTR_OPTIONS]
    } == {
        "auto": "Automatic",
        "auto_cool": "Cooling",
        "auto_heat": "Heating",
        "setup": "Setup",
        "standby": "Standby",
        "summer": "Summer mode (hot water only)",
    }
    assert operating_mode.attributes[ATTR_FRIENDLY_NAME] == "Control unit Operating mode"

    cpu_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_cpu_usage")
    assert isinstance(cpu_usage, State)
    assert cpu_usage.state == "2.7"
    assert cpu_usage.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert cpu_usage.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert cpu_usage.attributes[ATTR_FRIENDLY_NAME] == "Control unit CPU usage"

    webview_cpu_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_webview_cpu_usage")
    assert isinstance(webview_cpu_usage, State)
    assert webview_cpu_usage.state == "3.4"
    assert webview_cpu_usage.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert webview_cpu_usage.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert webview_cpu_usage.attributes[ATTR_FRIENDLY_NAME] == "Control unit WebView CPU usage"

    webserver_cpu_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_webserver_cpu_usage")
    assert isinstance(webserver_cpu_usage, State)
    assert webserver_cpu_usage.state == "6.7"
    assert webserver_cpu_usage.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert webserver_cpu_usage.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert webserver_cpu_usage.attributes[ATTR_FRIENDLY_NAME] == "Control unit WebServer CPU usage"

    control_cpu_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_control_cpu_usage")
    assert isinstance(control_cpu_usage, State)
    assert control_cpu_usage.state == "0.7"
    assert control_cpu_usage.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert control_cpu_usage.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert control_cpu_usage.attributes[ATTR_FRIENDLY_NAME] == "Control unit Ctrl CPU usage"

    ram_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_ram_usage")
    assert isinstance(ram_usage, State)
    assert ram_usage.state == "6432"
    assert ram_usage.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfInformation.KILOBYTES
    assert ram_usage.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert ram_usage.attributes[ATTR_FRIENDLY_NAME] == "Control unit RAM usage"

    free_ram: State | None = hass.states.get("sensor.keba_keenergy_12345678_free_ram")
    assert isinstance(free_ram, State)
    assert free_ram.state == "100060"
    assert free_ram.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfInformation.KILOBYTES
    assert free_ram.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert free_ram.attributes[ATTR_FRIENDLY_NAME] == "Control unit Free RAM"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_system_sensors_translated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    outdoor_temperature: State | None = hass.states.get("sensor.keba_keenergy_12345678_outdoor_temperature")
    assert isinstance(outdoor_temperature, State)
    assert outdoor_temperature.attributes[ATTR_FRIENDLY_NAME] == "Bedieneinheit Außentemperatur"

    operating_mode: State | None = hass.states.get("sensor.keba_keenergy_12345678_operating_mode")
    assert isinstance(operating_mode, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_system.state.{opt}"]
        for opt in operating_mode.attributes[ATTR_OPTIONS]
    } == {
        "auto": "Automatik",
        "auto_cool": "Kühlen",
        "auto_heat": "Heizen",
        "setup": "Einrichtung",
        "standby": "Standby",
        "summer": "Sommerbetrieb (nur Warmwasser)",
    }
    assert operating_mode.attributes[ATTR_FRIENDLY_NAME] == "Bedieneinheit Betriebsart"

    cpu_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_cpu_usage")
    assert isinstance(cpu_usage, State)
    assert cpu_usage.attributes[ATTR_FRIENDLY_NAME] == "Bedieneinheit CPU-Auslastung"

    webview_cpu_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_webview_cpu_usage")
    assert isinstance(webview_cpu_usage, State)
    assert webview_cpu_usage.attributes[ATTR_FRIENDLY_NAME] == "Bedieneinheit WebView CPU-Auslastung"

    webserver_cpu_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_webserver_cpu_usage")
    assert isinstance(webserver_cpu_usage, State)
    assert webserver_cpu_usage.attributes[ATTR_FRIENDLY_NAME] == "Bedieneinheit WebServer CPU-Auslastung"

    control_cpu_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_control_cpu_usage")
    assert isinstance(control_cpu_usage, State)
    assert control_cpu_usage.attributes[ATTR_FRIENDLY_NAME] == "Bedieneinheit Ctrl CPU-Auslastung"

    ram_usage: State | None = hass.states.get("sensor.keba_keenergy_12345678_ram_usage")
    assert isinstance(ram_usage, State)
    assert ram_usage.attributes[ATTR_FRIENDLY_NAME] == "Bedieneinheit RAM-Verbrauch"

    free_ram: State | None = hass.states.get("sensor.keba_keenergy_12345678_free_ram")
    assert isinstance(free_ram, State)
    assert free_ram.attributes[ATTR_FRIENDLY_NAME] == "Bedieneinheit Freier RAM"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_buffer_tank_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    buffer_tank_current_top_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_current_top_temperature_2",
    )
    assert isinstance(buffer_tank_current_top_temperature_1, State)
    assert buffer_tank_current_top_temperature_1.state == "35.67"
    assert buffer_tank_current_top_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert buffer_tank_current_top_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert buffer_tank_current_top_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        buffer_tank_current_top_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "Buffer tank 2 Current temperature (top)"
    )

    buffer_tank_current_bottom_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_current_bottom_temperature_1",
    )
    assert isinstance(buffer_tank_current_bottom_temperature_1, State)
    assert buffer_tank_current_bottom_temperature_1.state == "15.67"
    assert buffer_tank_current_bottom_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert buffer_tank_current_bottom_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert buffer_tank_current_bottom_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        buffer_tank_current_bottom_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "Buffer tank 1 Current temperature (bottom)"
    )

    buffer_tank_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_operating_mode_1",
    )
    assert isinstance(buffer_tank_operating_mode_1, State)
    assert buffer_tank_operating_mode_1.state == "off"
    assert buffer_tank_operating_mode_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert buffer_tank_operating_mode_1.attributes[ATTR_OPTIONS] == ["off", "on", "heat_up"]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_buffer_tank.state.{opt}"]
        for opt in buffer_tank_operating_mode_1.attributes[ATTR_OPTIONS]
    } == {
        "heat_up": "Heat up",
        "off": "Off",
        "on": "On",
    }
    assert buffer_tank_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Buffer tank 1 Operating mode"

    buffer_tank_standby_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_standby_temperature_1",
    )
    assert isinstance(buffer_tank_standby_temperature_1, State)
    assert buffer_tank_standby_temperature_1.state == "10.0"
    assert buffer_tank_standby_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert buffer_tank_standby_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert buffer_tank_standby_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert buffer_tank_standby_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Buffer tank 1 Standby temperature"

    buffer_tank_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_target_temperature_1",
    )
    assert isinstance(buffer_tank_target_temperature_1, State)
    assert buffer_tank_target_temperature_1.state == "44.0"
    assert buffer_tank_target_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert buffer_tank_target_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert buffer_tank_target_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert buffer_tank_target_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Buffer tank 1 Target temperature"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_buffer_tank_sensors_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    buffer_tank_current_top_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_current_top_temperature_2",
    )
    assert isinstance(buffer_tank_current_top_temperature_1, State)
    assert (
        buffer_tank_current_top_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Pufferspeicher 2 Ist-Temperatur (oben)"
    )

    buffer_tank_current_bottom_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_current_bottom_temperature_1",
    )
    assert isinstance(buffer_tank_current_bottom_temperature_1, State)
    assert (
        buffer_tank_current_bottom_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "Pufferspeicher 1 Ist-Temperatur (unten)"
    )

    buffer_tank_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_operating_mode_1",
    )
    assert isinstance(buffer_tank_operating_mode_1, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_buffer_tank.state.{opt}"]
        for opt in buffer_tank_operating_mode_1.attributes[ATTR_OPTIONS]
    } == {
        "heat_up": "Aufheizen",
        "off": "Aus",
        "on": "Ein",
    }
    assert buffer_tank_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Pufferspeicher 1 Betriebsart"

    buffer_tank_standby_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_standby_temperature_1",
    )
    assert isinstance(buffer_tank_standby_temperature_1, State)
    assert buffer_tank_standby_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Pufferspeicher 1 Stütztemperatur"

    buffer_tank_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_buffer_tank_target_temperature_1",
    )
    assert isinstance(buffer_tank_target_temperature_1, State)
    assert buffer_tank_target_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Pufferspeicher 1 Soll-Temperatur"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_hot_water_tank_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    hot_water_tank_current_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_current_temperature_1",
    )
    assert isinstance(hot_water_tank_current_temperature_1, State)
    assert hot_water_tank_current_temperature_1.state == "47.7"
    assert hot_water_tank_current_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_current_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert hot_water_tank_current_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_current_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 1 Current temperature"

    hot_water_tank_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_1",
    )
    assert isinstance(hot_water_tank_operating_mode_1, State)
    assert hot_water_tank_operating_mode_1.state == "heat_up"
    assert hot_water_tank_operating_mode_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert hot_water_tank_operating_mode_1.attributes[ATTR_OPTIONS] == ["off", "auto", "on", "heat_up"]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_hot_water_tank.state.{opt}"]
        for opt in hot_water_tank_operating_mode_1.attributes[ATTR_OPTIONS]
    } == {
        "heat_up": "Heat up",
        "auto": "Auto",
        "off": "Off",
        "on": "On",
    }
    assert hot_water_tank_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 1 Operating mode"

    hot_water_tank_min_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_standby_temperature_1",
    )
    assert isinstance(hot_water_tank_min_temperature_1, State)
    assert hot_water_tank_min_temperature_1.state == "32.5"
    assert hot_water_tank_min_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_min_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert hot_water_tank_min_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_min_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 1 Standby temperature"

    hot_water_tank_fresh_water_module_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_fresh_water_module_temperature_1",
    )
    assert isinstance(hot_water_tank_fresh_water_module_temperature_1, State)
    assert hot_water_tank_fresh_water_module_temperature_1.state == "51.23"
    assert (
        hot_water_tank_fresh_water_module_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT]
        == UnitOfTemperature.CELSIUS
    )
    assert hot_water_tank_fresh_water_module_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert (
        hot_water_tank_fresh_water_module_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    )
    assert (
        hot_water_tank_fresh_water_module_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "Hot water tank 1 Fresh water module temperature"
    )

    hot_water_tank_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
    )
    assert isinstance(hot_water_tank_target_temperature_1, State)
    assert hot_water_tank_target_temperature_1.state == "51.0"
    assert hot_water_tank_target_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_target_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert hot_water_tank_target_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_target_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 1 Target temperature"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_hot_water_tank_sensors_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    hot_water_tank_current_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_current_temperature_1",
    )
    assert isinstance(hot_water_tank_current_temperature_1, State)
    assert hot_water_tank_current_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 1 Ist-Temperatur"

    hot_water_tank_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_operating_mode_1",
    )
    assert isinstance(hot_water_tank_operating_mode_1, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_hot_water_tank.state.{opt}"]
        for opt in hot_water_tank_operating_mode_1.attributes[ATTR_OPTIONS]
    } == {
        "auto": "Auto",
        "heat_up": "Aufheizen",
        "off": "Aus",
        "on": "Ein",
    }
    assert hot_water_tank_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 1 Betriebsart"

    hot_water_tank_standby_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_standby_temperature_1",
    )
    assert isinstance(hot_water_tank_standby_temperature_1, State)
    assert hot_water_tank_standby_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 1 Stütztemperatur"

    hot_water_tank_fresh_water_module_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_fresh_water_module_temperature_1",
    )
    assert isinstance(hot_water_tank_fresh_water_module_temperature_1, State)
    assert hot_water_tank_fresh_water_module_temperature_1.state == "51.23"
    assert (
        hot_water_tank_fresh_water_module_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "Warmwasserspeicher 1 Frischwassermodul-Temperatur"
    )

    hot_water_tank_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
    )
    assert isinstance(hot_water_tank_target_temperature_1, State)
    assert hot_water_tank_target_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 1 Soll-Temperatur"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_pump_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

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
        "pump_down",
        "shutdown",
        "error",
    ]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.state.state.{opt}"]
        for opt in heat_pump_state.attributes[ATTR_OPTIONS]
    } == {
        "auto_cool": "Cooling",
        "auto_heat": "Heating",
        "defrost": "Defrost",
        "error": "Error",
        "flow": "Flow",
        "inflow": "Inflow",
        "pump_down": "Pump down",
        "shutdown": "Shutdown",
        "standby": "Standby",
    }
    assert heat_pump_state.attributes[ATTR_FRIENDLY_NAME] == "Heat pump State"

    heat_pump_substate: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_substate")
    assert isinstance(heat_pump_substate, State)
    assert heat_pump_substate.state == "oil_preheating"
    assert heat_pump_substate.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_pump_substate.attributes[ATTR_OPTIONS] == [
        "none",
        "oil_preheating",
        "pump_pre_run",
        "random_delay",
        "pressure_equalization",
        "defrost_pre_flow",
        "defrost_monitoring",
        "snow_detection",
        "flushing",
        "defrost_initialization",
        "preheat_flow",
        "defrost",
        "drip",
        "defrost_end",
        "open",
        "compressor_post_run",
        "pump_post_run",
        "lubrication_pulse",
        "reduced_speed",
        "compressor_delay",
        "defrost_venting",
        "switch_heating_cooling",
        "wait_for_compressor",
        "compressor_stop",
        "bivalent_lock",
        "locked",
        "return_flow_off",
        "mixer_open",
        "zone_valve",
        "electric_defrost",
        "counterflow_valve",
    ]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.substate.state.{opt}"]
        for opt in heat_pump_substate.attributes[ATTR_OPTIONS]
    } == {
        "bivalent_lock": "Bivalent lock",
        "compressor_delay": "Compressor delay",
        "compressor_post_run": "Compressor post-run",
        "compressor_stop": "Compressor stop",
        "counterflow_valve": "Counterflow valve",
        "defrost": "Defrost",
        "defrost_end": "Defrost end",
        "defrost_initialization": "Defrost initialization",
        "defrost_monitoring": "Defrost monitoring",
        "defrost_pre_flow": "Defrost pre-flow",
        "defrost_venting": "Defrost venting",
        "drip": "Drip",
        "electric_defrost": "Electric defrost",
        "flushing": "Flushing",
        "locked": "Locked",
        "lubrication_pulse": "Lubrication pulse",
        "mixer_open": "Mixer open",
        "none": "-",
        "oil_preheating": "Oil preheating",
        "open": "Open",
        "preheat_flow": "Preheat flow",
        "pressure_equalization": "Pressure equalization",
        "pump_post_run": "Pump post-run",
        "pump_pre_run": "Pump pre-run",
        "random_delay": "Random delay",
        "reduced_speed": "Reduced speed",
        "return_flow_off": "Return flow off",
        "snow_detection": "Snow detection",
        "switch_heating_cooling": "Switch heating/cooling",
        "wait_for_compressor": "Waiting for compressor",
        "zone_valve": "Zone valve",
    }
    assert heat_pump_substate.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Substate"

    heat_pump_circulation_pump: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_circulation_pump",
    )
    assert isinstance(heat_pump_circulation_pump, State)
    assert heat_pump_circulation_pump.state == "0.0"
    assert heat_pump_circulation_pump.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert heat_pump_circulation_pump.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_circulation_pump.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Circulation pump speed"

    heat_pump_flow_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_flow_temperature",
    )
    assert isinstance(heat_pump_flow_temperature, State)
    assert heat_pump_flow_temperature.state == "24.8"
    assert heat_pump_flow_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_flow_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_flow_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_flow_temperature.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Flow temperature"

    heat_pump_return_flow_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_return_flow_temperature",
    )
    assert isinstance(heat_pump_return_flow_temperature, State)
    assert heat_pump_return_flow_temperature.state == "23.9"
    assert heat_pump_return_flow_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_return_flow_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_return_flow_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_return_flow_temperature.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Return flow temperature"

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

    source_pump_speed: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_source_pump_speed")
    assert isinstance(source_pump_speed, State)
    assert source_pump_speed.state == "45.0"
    assert source_pump_speed.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert source_pump_speed.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert source_pump_speed.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Source pump speed"

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
    assert heat_pump_compressor.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Compressor speed"

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

    heat_pump_compressor_power: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_compressor_power",
    )
    assert isinstance(heat_pump_compressor_power, State)
    assert heat_pump_compressor_power.state == "5.52"
    assert heat_pump_compressor_power.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPower.WATT
    assert heat_pump_compressor_power.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_compressor_power.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.POWER
    assert heat_pump_compressor_power.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Compressor power"

    heat_pump_condenser_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_condenser_temperature",
    )
    assert isinstance(heat_pump_condenser_temperature, State)
    assert heat_pump_condenser_temperature.state == "31.51"
    assert heat_pump_condenser_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_condenser_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_condenser_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_condenser_temperature.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Condensation temperature"

    heat_pump_heating_power: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_power")
    assert isinstance(heat_pump_heating_power, State)
    assert heat_pump_heating_power.state == "3.22"
    assert heat_pump_heating_power.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPower.WATT
    assert heat_pump_heating_power.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_heating_power.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.POWER
    assert heat_pump_heating_power.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heating power"

    heat_pump_hot_water_power: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_hot_water_power")
    assert isinstance(heat_pump_hot_water_power, State)
    assert heat_pump_hot_water_power.state == "2.77"
    assert heat_pump_hot_water_power.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPower.WATT
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
    assert heat_pump_heating_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert heat_pump_heating_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_heating_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heating energy"

    heat_pump_heating_energy_consumption: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_heating_energy_consumption",
    )
    assert isinstance(heat_pump_heating_energy_consumption, State)
    assert heat_pump_heating_energy_consumption.state == "7.33"
    assert heat_pump_heating_energy_consumption.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_heating_energy_consumption.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert heat_pump_heating_energy_consumption.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_heating_energy_consumption.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heating energy consumption"

    heat_pump_heating_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_spf")
    assert isinstance(heat_pump_heating_spf, State)
    assert heat_pump_heating_spf.state == "3.32"
    assert heat_pump_heating_spf.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_heating_spf.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heating SPF"

    heat_pump_cooling_energy: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cooling_energy")
    assert isinstance(heat_pump_cooling_energy, State)
    assert heat_pump_cooling_energy.state == "7.21"
    assert heat_pump_cooling_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_cooling_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert heat_pump_cooling_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_cooling_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Cooling energy"

    heat_pump_cooling_energy_consumption: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_cooling_energy_consumption",
    )
    assert isinstance(heat_pump_cooling_energy_consumption, State)
    assert heat_pump_cooling_energy_consumption.state == "8.72"
    assert heat_pump_cooling_energy_consumption.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_cooling_energy_consumption.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert heat_pump_cooling_energy_consumption.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_cooling_energy_consumption.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Cooling energy consumption"

    heat_pump_cooling_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cooling_spf")
    assert isinstance(heat_pump_cooling_spf, State)
    assert heat_pump_cooling_spf.state == "4.22"
    assert heat_pump_cooling_spf.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_cooling_spf.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Cooling SPF"

    heat_pump_hot_water_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_energy",
    )
    assert isinstance(heat_pump_hot_water_energy, State)
    assert heat_pump_hot_water_energy.state == "7.86"
    assert heat_pump_hot_water_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_hot_water_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert heat_pump_hot_water_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_hot_water_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Hot water energy"

    heat_pump_hot_water_energy_consumption: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_energy_consumption",
    )
    assert isinstance(heat_pump_hot_water_energy_consumption, State)
    assert heat_pump_hot_water_energy_consumption.state == "2.77"
    assert heat_pump_hot_water_energy_consumption.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_hot_water_energy_consumption.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert heat_pump_hot_water_energy_consumption.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert (
        heat_pump_hot_water_energy_consumption.attributes[ATTR_FRIENDLY_NAME]
        == "Heat pump Hot water energy consumption"
    )

    heat_pump_hot_water_spf: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_spf",
    )
    assert isinstance(heat_pump_hot_water_spf, State)
    assert heat_pump_hot_water_spf.state == "2.5"
    assert heat_pump_hot_water_spf.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_hot_water_spf.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Hot water SPF"

    heat_pump_total_thermal_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_total_thermal_energy",
    )
    assert isinstance(heat_pump_total_thermal_energy, State)
    assert heat_pump_total_thermal_energy.state == "8.22"
    assert heat_pump_total_thermal_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_total_thermal_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert heat_pump_total_thermal_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_total_thermal_energy.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Total thermal energy"

    heat_pump_total_energy_consumption: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_total_energy_consumption",
    )
    assert isinstance(heat_pump_total_energy_consumption, State)
    assert heat_pump_total_energy_consumption.state == "5.21"
    assert heat_pump_total_energy_consumption.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert heat_pump_total_energy_consumption.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert heat_pump_total_energy_consumption.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert heat_pump_total_energy_consumption.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Total energy consumption"

    heat_pump_total_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_total_spf")
    assert isinstance(heat_pump_total_spf, State)
    assert heat_pump_total_spf.state == "2.43"
    assert heat_pump_total_spf.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_total_spf.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Total SPF"

    heat_pump_operating_time: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_operating_time",
    )
    assert isinstance(heat_pump_operating_time, State)
    assert heat_pump_operating_time.state == "1058.06"
    assert heat_pump_operating_time.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTime.HOURS
    assert heat_pump_operating_time.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert heat_pump_operating_time.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.DURATION
    assert heat_pump_operating_time.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Operating time"

    heat_pump_max_runtime: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_max_runtime",
    )
    assert isinstance(heat_pump_max_runtime, State)
    assert heat_pump_max_runtime.state == "167.33"
    assert heat_pump_max_runtime.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTime.HOURS
    assert heat_pump_max_runtime.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_max_runtime.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.DURATION
    assert heat_pump_max_runtime.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Maximum runtime"

    heat_pump_vaporizer_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_vaporizer_temperature",
    )
    assert isinstance(heat_pump_vaporizer_temperature, State)
    assert heat_pump_vaporizer_temperature.state == "-4.56"
    assert heat_pump_vaporizer_temperature.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_vaporizer_temperature.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_vaporizer_temperature.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_vaporizer_temperature.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Vaporization temperature"

    heat_pump_target_overheating: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_target_overheating",
    )
    assert isinstance(heat_pump_target_overheating, State)
    assert heat_pump_target_overheating.state == "5.5"
    assert heat_pump_target_overheating.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_target_overheating.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_target_overheating.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_target_overheating.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Target overheating"

    heat_pump_current_overheating: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_current_overheating",
    )
    assert isinstance(heat_pump_current_overheating, State)
    assert heat_pump_current_overheating.state == "18.68"
    assert heat_pump_current_overheating.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_pump_current_overheating.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_pump_current_overheating.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_pump_current_overheating.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Current overheating"

    heat_pump_expansion_valve_position: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_expansion_valve_position",
    )
    assert isinstance(heat_pump_expansion_valve_position, State)
    assert heat_pump_expansion_valve_position.state == "20"
    assert heat_pump_expansion_valve_position.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Expansion valve position"

    heat_pump_activation_counter: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_activation_counter",
    )
    assert isinstance(heat_pump_activation_counter, State)
    assert heat_pump_activation_counter.state == "477"
    assert heat_pump_activation_counter.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert heat_pump_activation_counter.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Activation counter"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_pump_sensors_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    heat_pump_state: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_state")
    assert isinstance(heat_pump_state, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.state.state.{opt}"]
        for opt in heat_pump_state.attributes[ATTR_OPTIONS]
    } == {
        "auto_cool": "Kühlen",
        "auto_heat": "Heizen",
        "defrost": "Abtauen",
        "error": "Fehler",
        "flow": "Vorlauf",
        "inflow": "Nachlauf",
        "pump_down": "Pump-Down-Vorgang",
        "shutdown": "Herunterfahren",
        "standby": "Standby",
    }
    assert heat_pump_state.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Status"

    heat_pump_substate: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_substate")
    assert isinstance(heat_pump_substate, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.substate.state.{opt}"]
        for opt in heat_pump_substate.attributes[ATTR_OPTIONS]
    } == {
        "bivalent_lock": "Bivalente Sperre",
        "compressor_delay": "Kompressorverzögerung",
        "compressor_post_run": "Kompressornachlauf",
        "compressor_stop": "Kompressorstopp",
        "counterflow_valve": "Gegenstromventil",
        "defrost": "Abtauen",
        "defrost_end": "Abtauende",
        "defrost_initialization": "Abtauinitialisierung",
        "defrost_monitoring": "Abtauüberwachung",
        "defrost_pre_flow": "Abtauvorlauf",
        "defrost_venting": "Abtaulüften",
        "drip": "Abtropfen",
        "electric_defrost": "Elektrisches Abtauen",
        "flushing": "Spülen",
        "locked": "Gesperrt",
        "lubrication_pulse": "Schmierimpuls",
        "mixer_open": "Mischer offen",
        "none": "-",
        "oil_preheating": "Ölvorwärmung",
        "open": "Öffnen",
        "preheat_flow": "Heizvorlauf",
        "pressure_equalization": "Druckausgleich",
        "pump_post_run": "Pumpennachlauf",
        "pump_pre_run": "Pumpenvorlauf",
        "random_delay": "Zufallsverzögerung",
        "reduced_speed": "Reduzierte Geschwindigkeit",
        "return_flow_off": "Rücklauf aus",
        "snow_detection": "Schneeerkennung",
        "switch_heating_cooling": "Umschalten Heizen/Kühlen",
        "wait_for_compressor": "Warten auf Kompressor",
        "zone_valve": "Zonenventil",
    }
    assert heat_pump_substate.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Unterstatus"

    heat_pump_circulation_pump: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_circulation_pump",
    )
    assert isinstance(heat_pump_circulation_pump, State)
    assert heat_pump_circulation_pump.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Umwälzpumpedrehzahl"

    heat_pump_flow_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_flow_temperature",
    )
    assert isinstance(heat_pump_flow_temperature, State)
    assert heat_pump_flow_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Vorlauftemperatur"

    heat_pump_return_flow_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_return_flow_temperature",
    )
    assert isinstance(heat_pump_return_flow_temperature, State)
    assert heat_pump_return_flow_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Rücklauftemperatur"

    heat_pump_source_input_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_source_input_temperature",
    )
    assert isinstance(heat_pump_source_input_temperature, State)
    assert heat_pump_source_input_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Quelle-Eingangstemperatur"

    heat_pump_source_output_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_source_output_temperature",
    )
    assert isinstance(heat_pump_source_output_temperature, State)
    assert heat_pump_source_output_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Quelle-Ausgangstemperatur"

    source_pump_speed: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_source_pump_speed")
    assert isinstance(source_pump_speed, State)
    assert source_pump_speed.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Quellenpumpendrehzahl"

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
    assert heat_pump_compressor.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Kompressordrehzahl"

    heat_pump_high_pressure: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_high_pressure")
    assert isinstance(heat_pump_high_pressure, State)
    assert heat_pump_high_pressure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Hochdruck"

    heat_pump_low_pressure: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_low_pressure")
    assert isinstance(heat_pump_low_pressure, State)
    assert heat_pump_low_pressure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Niederdruck"

    heat_pump_compressor_power: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_compressor_power",
    )
    assert isinstance(heat_pump_compressor_power, State)
    assert heat_pump_compressor_power.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Leistung Kompressor"

    heat_pump_condenser_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_condenser_temperature",
    )
    assert isinstance(heat_pump_condenser_temperature, State)
    assert heat_pump_condenser_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Kondensationstemperatur"

    heat_pump_heating_power: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_power")
    assert isinstance(heat_pump_heating_power, State)
    assert heat_pump_heating_power.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Leistung Heizen"

    heat_pump_hot_water_power: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_hot_water_power")
    assert isinstance(heat_pump_hot_water_power, State)
    assert heat_pump_hot_water_power.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Leistung Warmwasser"

    heat_pump_cop: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cop")
    assert isinstance(heat_pump_cop, State)
    assert heat_pump_cop.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Leistungszahl"

    heat_pump_heating_energy: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_energy")
    assert isinstance(heat_pump_heating_energy, State)
    assert heat_pump_heating_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Wärmemenge"

    heat_pump_heating_energy_consumption: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_heating_energy_consumption",
    )
    assert isinstance(heat_pump_heating_energy_consumption, State)
    assert heat_pump_heating_energy_consumption.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Energieverbrauch Heizen"

    heat_pump_heating_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_heating_spf")
    assert isinstance(heat_pump_heating_spf, State)
    assert heat_pump_heating_spf.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe JAZ Heizen"

    heat_pump_cooling_energy: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cooling_energy")
    assert isinstance(heat_pump_cooling_energy, State)
    assert heat_pump_cooling_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Kühlmenge"

    heat_pump_cooling_energy_consumption: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_cooling_energy_consumption",
    )
    assert isinstance(heat_pump_cooling_energy_consumption, State)
    assert heat_pump_cooling_energy_consumption.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Energieverbrauch Kühlen"

    heat_pump_cooling_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_cooling_spf")
    assert isinstance(heat_pump_cooling_spf, State)
    assert heat_pump_cooling_spf.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe JAZ Kühlen"

    heat_pump_hot_water_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_energy",
    )
    assert isinstance(heat_pump_hot_water_energy, State)
    assert heat_pump_hot_water_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Warmwasserwärmemenge"

    heat_pump_hot_water_energy_consumption: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_energy_consumption",
    )
    assert isinstance(heat_pump_hot_water_energy_consumption, State)
    assert (
        heat_pump_hot_water_energy_consumption.attributes[ATTR_FRIENDLY_NAME]
        == "Wärmepumpe Energieverbrauch Warmwasser"
    )

    heat_pump_hot_water_spf: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_hot_water_spf",
    )
    assert isinstance(heat_pump_hot_water_spf, State)
    assert heat_pump_hot_water_spf.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe JAZ Warmwasser"

    heat_pump_total_thermal_energy: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_total_thermal_energy",
    )
    assert isinstance(heat_pump_total_thermal_energy, State)
    assert heat_pump_total_thermal_energy.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Gesamtwärmemenge"

    heat_pump_total_energy_consumption: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_total_energy_consumption",
    )
    assert isinstance(heat_pump_total_energy_consumption, State)
    assert heat_pump_total_energy_consumption.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Stromverbrauch gesamt"

    heat_pump_total_spf: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_pump_total_spf")
    assert isinstance(heat_pump_total_spf, State)
    assert heat_pump_total_spf.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe JAZ gesamt"

    heat_pump_operating_time: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_operating_time",
    )
    assert isinstance(heat_pump_operating_time, State)
    assert heat_pump_operating_time.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Betriebsstunden"

    heat_pump_max_runtime: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_max_runtime",
    )
    assert isinstance(heat_pump_max_runtime, State)
    assert heat_pump_max_runtime.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Maximale Laufzeit"

    heat_pump_vaporizer_temperature: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_vaporizer_temperature",
    )
    assert isinstance(heat_pump_vaporizer_temperature, State)
    assert heat_pump_vaporizer_temperature.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Verdampfungstemperatur"

    heat_pump_target_overheating: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_target_overheating",
    )
    assert isinstance(heat_pump_target_overheating, State)
    assert heat_pump_target_overheating.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Sollüberhitzung"

    heat_pump_current_overheating: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_current_overheating",
    )
    assert isinstance(heat_pump_current_overheating, State)
    assert heat_pump_current_overheating.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Istüberhitzung"

    heat_pump_expansion_valve_position: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_expansion_valve_position",
    )
    assert isinstance(heat_pump_expansion_valve_position, State)
    assert heat_pump_expansion_valve_position.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Expansionsventil"

    heat_pump_activation_counter: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_pump_activation_counter",
    )
    assert isinstance(heat_pump_activation_counter, State)
    assert heat_pump_activation_counter.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Einschaltvorgänge"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_circuit_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    heat_circuit_heating_curve_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heating_curve_1",
    )
    assert isinstance(heat_circuit_heating_curve_1, State)
    assert heat_circuit_heating_curve_1.state == "hc6"
    assert heat_circuit_heating_curve_1.attributes[ATTR_OPTIONS] == [
        "hc1",
        "hc2",
        "hc3",
        "hc4",
        "hc5",
        "hc6",
        "hc7",
        "hc8",
        "hc_fbh",
        "hc_hk",
    ]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.heating_curve.state.{opt}"]
        for opt in heat_circuit_heating_curve_1.attributes[ATTR_OPTIONS]
    } == {
        "hc1": "1",
        "hc2": "2",
        "hc3": "3",
        "hc4": "4",
        "hc5": "5",
        "hc6": "6",
        "hc7": "7",
        "hc8": "8",
        "hc_fbh": "Underfloor heating",
        "hc_hk": "Radiator heating",
    }
    assert heat_circuit_heating_curve_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_circuit_heating_curve_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Heating curve"

    heat_circuit_room_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_1",
    )
    assert isinstance(heat_circuit_room_temperature_1, State)
    assert heat_circuit_room_temperature_1.state == "22.42"
    assert heat_circuit_room_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_room_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_room_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_room_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Room temperature"

    heat_circuit_room_humidity_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_room_humidity_1",
    )
    assert isinstance(heat_circuit_room_humidity_1, State)
    assert heat_circuit_room_humidity_1.state == "53.0"
    assert heat_circuit_room_humidity_1.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert heat_circuit_room_humidity_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_room_humidity_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.HUMIDITY
    assert heat_circuit_room_humidity_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Room humidity"

    heat_circuit_dew_point_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_dew_point_1",
    )
    assert isinstance(heat_circuit_dew_point_1, State)
    assert heat_circuit_dew_point_1.state == "13.1"
    assert heat_circuit_dew_point_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_dew_point_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_dew_point_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_dew_point_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Dew point"

    heat_circuit_flow_temperature_setpoint_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_setpoint_1",
    )
    assert isinstance(heat_circuit_flow_temperature_setpoint_1, State)
    assert heat_circuit_flow_temperature_setpoint_1.state == "26.55"
    assert heat_circuit_flow_temperature_setpoint_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_flow_temperature_setpoint_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_flow_temperature_setpoint_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_flow_temperature_setpoint_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Flow temperature setpoint"
    )

    heat_circuit_flow_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_1",
    )
    assert isinstance(heat_circuit_flow_temperature_1, State)
    assert heat_circuit_flow_temperature_1.state == "24.34"
    assert heat_circuit_flow_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_flow_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_flow_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_flow_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Flow temperature"

    heat_circuit_return_flow_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_return_flow_temperature_1",
    )
    assert isinstance(heat_circuit_return_flow_temperature_1, State)
    assert heat_circuit_return_flow_temperature_1.state == "22.21"
    assert heat_circuit_return_flow_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_return_flow_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_return_flow_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_return_flow_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Return flow temperature"
    )

    heat_circuit_selected_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_selected_target_temperature_1",
    )
    assert isinstance(heat_circuit_selected_target_temperature_1, State)
    assert heat_circuit_selected_target_temperature_1.state == "20.0"
    assert heat_circuit_selected_target_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_selected_target_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_selected_target_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_selected_target_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Target room temperature (selected)"
    )

    heat_circuit_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_1",
    )
    assert isinstance(heat_circuit_target_temperature_1, State)
    assert heat_circuit_target_temperature_1.state == "20.5"
    assert heat_circuit_target_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_target_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_target_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_target_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Target room temperature"
    )

    heat_circuit_target_temperature_day_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
    )
    assert isinstance(heat_circuit_target_temperature_day_1, State)
    assert heat_circuit_target_temperature_day_1.state == "20.5"
    assert heat_circuit_target_temperature_day_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_target_temperature_day_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_target_temperature_day_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_target_temperature_day_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Target temperature (day)"
    )

    heat_circuit_heating_limit_day_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_day_1",
    )
    assert isinstance(heat_circuit_heating_limit_day_1, State)
    assert heat_circuit_heating_limit_day_1.state == "20.0"
    assert heat_circuit_heating_limit_day_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_heating_limit_day_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_heating_limit_day_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert heat_circuit_heating_limit_day_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Heating limit (day)"

    heat_circuit_target_temperature_night_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_night_1",
    )
    assert isinstance(heat_circuit_target_temperature_night_1, State)
    assert heat_circuit_target_temperature_night_1.state == "20.0"
    assert heat_circuit_target_temperature_night_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_target_temperature_night_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_target_temperature_night_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_target_temperature_night_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Target temperature (night)"
    )

    heat_circuit_heating_limit_night_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_night_1",
    )
    assert isinstance(heat_circuit_heating_limit_night_1, State)
    assert heat_circuit_heating_limit_night_1.state == "18.0"
    assert heat_circuit_heating_limit_night_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_heating_limit_night_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_heating_limit_night_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_heating_limit_night_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Heating limit (night)"
    )

    heat_circuit_target_temperature_away_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_away_1",
    )
    assert isinstance(heat_circuit_target_temperature_away_1, State)
    assert heat_circuit_target_temperature_away_1.state == "18.0"
    assert heat_circuit_target_temperature_away_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_target_temperature_away_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_target_temperature_away_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_target_temperature_away_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Target temperature (away)"
    )

    heat_circuit_target_temperature_offset_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1",
    )
    assert isinstance(heat_circuit_target_temperature_offset_1, State)
    assert heat_circuit_target_temperature_offset_1.state == "1.5"
    assert heat_circuit_target_temperature_offset_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_target_temperature_offset_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert heat_circuit_target_temperature_offset_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_target_temperature_offset_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Target temperature (offset)"
    )

    heat_circuit_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1",
    )
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.state == "day"
    assert heat_circuit_operating_mode_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_circuit_operating_mode_1.attributes[ATTR_OPTIONS] == [
        "off",
        "auto",
        "day",
        "night",
        "holiday",
        "party",
        "external",
        "room_control",
    ]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_heat_circuit.state.{opt}"]
        for opt in heat_circuit_operating_mode_1.attributes[ATTR_OPTIONS]
    } == {
        "auto": "Auto",
        "day": "Day",
        "external": "External",
        "holiday": "Away",
        "night": "Night",
        "off": "Off",
        "party": "Party",
        "room_control": "Room control",
    }
    assert heat_circuit_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Operating mode"

    heat_circuit_heat_request_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heat_request_1",
    )
    assert isinstance(heat_circuit_heat_request_1, State)
    assert heat_circuit_heat_request_1.state == STATE_ON
    assert heat_circuit_heat_request_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert heat_circuit_heat_request_1.attributes[ATTR_OPTIONS] == [
        "off",
        "on",
        "flow_off",
        "temporary_off",
        "room_off",
        "outdoor_off",
        "inflow_off",
    ]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.heat_request.state.{opt}"]
        for opt in heat_circuit_heat_request_1.attributes[ATTR_OPTIONS]
    } == {
        "flow_off": "Off (low flow temperature)",
        "inflow_off": "Off (high return flow temperature)",
        "off": "Off",
        "on": "On",
        "outdoor_off": "Off (high outside temperature)",
        "room_off": "Off (high room temperature)",
        "temporary_off": "Off (temporary)",
    }
    assert heat_circuit_heat_request_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Heat request"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_circuit_sensors_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    heat_circuit_heating_curve_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heating_curve_1",
    )
    assert isinstance(heat_circuit_heating_curve_1, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.heating_curve.state.{opt}"]
        for opt in heat_circuit_heating_curve_1.attributes[ATTR_OPTIONS]
    } == {
        "hc1": "1",
        "hc2": "2",
        "hc3": "3",
        "hc4": "4",
        "hc5": "5",
        "hc6": "6",
        "hc7": "7",
        "hc8": "8",
        "hc_fbh": "Fußbodenheizung",
        "hc_hk": "Heizkörper",
    }
    assert heat_circuit_heating_curve_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Heizkurve"

    heat_circuit_room_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_1",
    )
    assert isinstance(heat_circuit_room_temperature_1, State)
    assert heat_circuit_room_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Raumtemperatur"

    heat_circuit_room_humidity_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_room_humidity_1",
    )
    assert isinstance(heat_circuit_room_humidity_1, State)
    assert heat_circuit_room_humidity_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Raumluftfeuchtigkeit"

    heat_circuit_dew_point_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_dew_point_1",
    )
    assert isinstance(heat_circuit_dew_point_1, State)
    assert heat_circuit_dew_point_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Taupunkt"

    heat_circuit_flow_temperature_setpoint_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_setpoint_1",
    )
    assert isinstance(heat_circuit_flow_temperature_setpoint_1, State)
    assert (
        heat_circuit_flow_temperature_setpoint_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Soll-Vorlauftemperatur"
    )

    heat_circuit_flow_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_1",
    )
    assert isinstance(heat_circuit_flow_temperature_1, State)
    assert heat_circuit_flow_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Vorlauftemperatur"

    heat_circuit_return_flow_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_return_flow_temperature_1",
    )
    assert isinstance(heat_circuit_return_flow_temperature_1, State)
    assert heat_circuit_return_flow_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Rücklauftemperatur"

    heat_circuit_selected_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_selected_target_temperature_1",
    )
    assert isinstance(heat_circuit_selected_target_temperature_1, State)
    assert (
        heat_circuit_selected_target_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heizkreis 1 Soll-Raumtemperatur (ausgewählt)"
    )

    heat_circuit_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_1",
    )
    assert isinstance(heat_circuit_target_temperature_1, State)
    assert heat_circuit_target_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Soll-Raumtemperatur"

    heat_circuit_target_temperature_day_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
    )
    assert isinstance(heat_circuit_target_temperature_day_1, State)
    assert (
        heat_circuit_target_temperature_day_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Soll-Raumtemperatur (Tag)"
    )

    heat_circuit_heating_limit_day_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_day_1",
    )
    assert isinstance(heat_circuit_heating_limit_day_1, State)
    assert heat_circuit_heating_limit_day_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Heizgrenze (Tag)"

    heat_circuit_target_temperature_night_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_night_1",
    )
    assert isinstance(heat_circuit_target_temperature_night_1, State)
    assert (
        heat_circuit_target_temperature_night_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heizkreis 1 Soll-Raumtemperatur (Nacht)"
    )

    heat_circuit_heating_limit_night_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heating_limit_night_1",
    )
    assert isinstance(heat_circuit_heating_limit_night_1, State)
    assert heat_circuit_heating_limit_night_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Heizgrenze (Nacht)"

    heat_circuit_target_temperature_away_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_away_1",
    )
    assert isinstance(heat_circuit_target_temperature_away_1, State)
    assert (
        heat_circuit_target_temperature_away_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heizkreis 1 Soll-Raumtemperatur (Urlaub)"
    )

    heat_circuit_target_temperature_offset_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1",
    )
    assert isinstance(heat_circuit_target_temperature_offset_1, State)
    assert (
        heat_circuit_target_temperature_offset_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heizkreis 1 Soll-Raumtemperatur (Offset)"
    )

    heat_circuit_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1",
    )
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_heat_circuit.state.{opt}"]
        for opt in heat_circuit_operating_mode_1.attributes[ATTR_OPTIONS]
    } == {
        "auto": "Auto",
        "day": "Tag",
        "external": "Extern",
        "holiday": "Urlaub",
        "night": "Nacht",
        "off": "Aus",
        "party": "Party",
        "room_control": "Raumregelung",
    }
    assert heat_circuit_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Betriebsart"

    heat_circuit_heat_request_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_heat_request_1",
    )
    assert isinstance(heat_circuit_heat_request_1, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.heat_request.state.{opt}"]
        for opt in heat_circuit_heat_request_1.attributes[ATTR_OPTIONS]
    } == {
        "flow_off": "Aus (Niedrige Vorlauftemperatur)",
        "inflow_off": "Aus (Hohe Rücklauftemperatur)",
        "off": "Aus",
        "on": "Ein",
        "outdoor_off": "Aus (Hohe Außentemperatur)",
        "room_off": "Aus (Hohe Raumtemperatur)",
        "temporary_off": "Aus (Vorübergehend)",
    }
    assert heat_circuit_heat_request_1.attributes.get(ATTR_FRIENDLY_NAME) == "Heizkreis 1 Heizanforderung"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_solar_circuit_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    solar_circuit_source_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_source_temperature_1",
    )
    assert isinstance(solar_circuit_source_temperature_1, State)
    assert solar_circuit_source_temperature_1.state == "44.43"
    assert solar_circuit_source_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_source_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_source_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert solar_circuit_source_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Collector temperature"

    solar_circuit_source_temperature_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_source_temperature_2",
    )
    assert isinstance(solar_circuit_source_temperature_2, State)
    assert solar_circuit_source_temperature_2.state == "34.43"
    assert solar_circuit_source_temperature_2.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_source_temperature_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_source_temperature_2.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert solar_circuit_source_temperature_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Collector temperature"

    solar_circuit_pump_1_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_pump_1_1",
    )
    assert isinstance(solar_circuit_pump_1_1, State)
    assert solar_circuit_pump_1_1.state == "63.0"
    assert solar_circuit_pump_1_1.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert solar_circuit_pump_1_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_pump_1_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Pump 1"

    solar_circuit_pump_1_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_pump_1_2",
    )
    assert isinstance(solar_circuit_pump_1_2, State)
    assert solar_circuit_pump_1_2.state == "43.0"
    assert solar_circuit_pump_1_2.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert solar_circuit_pump_1_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_pump_1_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Pump 1"

    solar_circuit_pump_2_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_pump_2_1",
    )
    assert isinstance(solar_circuit_pump_2_1, State)
    assert solar_circuit_pump_2_1.state == "73.0"
    assert solar_circuit_pump_2_1.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert solar_circuit_pump_2_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_pump_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Pump 2"

    solar_circuit_pump_2_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_pump_2_2",
    )
    assert isinstance(solar_circuit_pump_2_2, State)
    assert solar_circuit_pump_2_2.state == "53.0"
    assert solar_circuit_pump_2_2.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert solar_circuit_pump_2_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_pump_2_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Pump 2"

    solar_circuit_current_temperature_1_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_1",
    )
    assert isinstance(solar_circuit_current_temperature_1_1, State)
    assert solar_circuit_current_temperature_1_1.state == "36.76"
    assert solar_circuit_current_temperature_1_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_current_temperature_1_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_current_temperature_1_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        solar_circuit_current_temperature_1_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Current temperature 1"
    )

    solar_circuit_current_temperature_1_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_2",
    )
    assert isinstance(solar_circuit_current_temperature_1_2, State)
    assert solar_circuit_current_temperature_1_2.state == "46.76"
    assert solar_circuit_current_temperature_1_2.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_current_temperature_1_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_current_temperature_1_2.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        solar_circuit_current_temperature_1_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Current temperature 1"
    )

    solar_circuit_current_temperature_2_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_1",
    )
    assert isinstance(solar_circuit_current_temperature_2_1, State)
    assert solar_circuit_current_temperature_2_1.state == "26.76"
    assert solar_circuit_current_temperature_2_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_current_temperature_2_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_current_temperature_2_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        solar_circuit_current_temperature_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Current temperature 2"
    )

    solar_circuit_current_temperature_2_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_2",
    )
    assert isinstance(solar_circuit_current_temperature_2_2, State)
    assert solar_circuit_current_temperature_2_2.state == "56.76"
    assert solar_circuit_current_temperature_2_2.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_current_temperature_2_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_current_temperature_2_2.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        solar_circuit_current_temperature_2_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Current temperature 2"
    )

    solar_circuit_target_temperature_1_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_1_1",
    )
    assert isinstance(solar_circuit_target_temperature_1_1, State)
    assert solar_circuit_target_temperature_1_1.state == "55.0"
    assert solar_circuit_target_temperature_1_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_target_temperature_1_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_target_temperature_1_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert solar_circuit_target_temperature_1_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Target temperature 1"

    solar_circuit_target_temperature_1_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_1_2",
    )
    assert isinstance(solar_circuit_target_temperature_1_2, State)
    assert solar_circuit_target_temperature_1_2.state == "53.0"
    assert solar_circuit_target_temperature_1_2.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_target_temperature_1_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_target_temperature_1_2.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert solar_circuit_target_temperature_1_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Target temperature 1"

    solar_circuit_target_temperature_2_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_2_1",
    )
    assert isinstance(solar_circuit_target_temperature_2_1, State)
    assert solar_circuit_target_temperature_2_1.state == "54.0"
    assert solar_circuit_target_temperature_2_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_target_temperature_2_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_target_temperature_2_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert solar_circuit_target_temperature_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Target temperature 2"

    solar_circuit_target_temperature_2_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_2_2",
    )
    assert isinstance(solar_circuit_target_temperature_2_2, State)
    assert solar_circuit_target_temperature_2_2.state == "52.0"
    assert solar_circuit_target_temperature_2_2.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert solar_circuit_target_temperature_2_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_target_temperature_2_2.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert solar_circuit_target_temperature_2_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Target temperature 2"

    solar_circuit_heating_energy_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_heating_energy_1",
    )
    assert isinstance(solar_circuit_heating_energy_1, State)
    assert solar_circuit_heating_energy_1.state == "8.73"
    assert solar_circuit_heating_energy_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert solar_circuit_heating_energy_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert solar_circuit_heating_energy_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert solar_circuit_heating_energy_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Heating energy"

    solar_circuit_heating_energy_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_heating_energy_2",
    )
    assert isinstance(solar_circuit_heating_energy_2, State)
    assert solar_circuit_heating_energy_2.state == "4.73"
    assert solar_circuit_heating_energy_2.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert solar_circuit_heating_energy_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert solar_circuit_heating_energy_2.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert solar_circuit_heating_energy_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Heating energy"

    solar_circuit_daily_energy_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_daily_energy_1",
    )
    assert isinstance(solar_circuit_daily_energy_1, State)
    assert solar_circuit_daily_energy_1.state == "2.33"
    assert solar_circuit_daily_energy_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert solar_circuit_daily_energy_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert solar_circuit_daily_energy_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert solar_circuit_daily_energy_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Daily energy"

    solar_circuit_daily_energy_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_daily_energy_2",
    )
    assert isinstance(solar_circuit_daily_energy_2, State)
    assert solar_circuit_daily_energy_2.state == "3.33"
    assert solar_circuit_daily_energy_2.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
    assert solar_circuit_daily_energy_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
    assert solar_circuit_daily_energy_2.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
    assert solar_circuit_daily_energy_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Daily energy"

    solar_circuit_actual_power_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_actual_power_1",
    )
    assert isinstance(solar_circuit_actual_power_1, State)
    assert solar_circuit_actual_power_1.state == "3452.0"
    assert solar_circuit_actual_power_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPower.WATT
    assert solar_circuit_actual_power_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_actual_power_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.POWER
    assert solar_circuit_actual_power_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Power"

    solar_circuit_actual_power_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_actual_power_2",
    )
    assert isinstance(solar_circuit_actual_power_2, State)
    assert solar_circuit_actual_power_2.state == "2452.0"
    assert solar_circuit_actual_power_2.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPower.WATT
    assert solar_circuit_actual_power_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert solar_circuit_actual_power_2.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.POWER
    assert solar_circuit_actual_power_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Power"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_solar_circuit_sensors_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    solar_circuit_source_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_source_temperature_1",
    )
    assert isinstance(solar_circuit_source_temperature_1, State)
    assert solar_circuit_source_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Kollektortemperatur"

    solar_circuit_source_temperature_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_source_temperature_2",
    )
    assert isinstance(solar_circuit_source_temperature_2, State)
    assert solar_circuit_source_temperature_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Kollektortemperatur"

    solar_circuit_pump_1_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_pump_1_1",
    )
    assert isinstance(solar_circuit_pump_1_1, State)
    assert solar_circuit_pump_1_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Pumpe 1"

    solar_circuit_pump_1_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_pump_1_2",
    )
    assert isinstance(solar_circuit_pump_1_2, State)
    assert solar_circuit_pump_1_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Pumpe 1"

    solar_circuit_pump_2_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_pump_2_1",
    )
    assert isinstance(solar_circuit_pump_2_1, State)
    assert solar_circuit_pump_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Pumpe 2"

    solar_circuit_pump_2_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_pump_2_2",
    )
    assert isinstance(solar_circuit_pump_2_2, State)
    assert solar_circuit_pump_2_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Pumpe 2"

    solar_circuit_current_temperature_1_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_1",
    )
    assert isinstance(solar_circuit_current_temperature_1_1, State)
    assert solar_circuit_current_temperature_1_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Ist-Temperatur 1"

    solar_circuit_current_temperature_1_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_2",
    )
    assert isinstance(solar_circuit_current_temperature_1_2, State)
    assert solar_circuit_current_temperature_1_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Ist-Temperatur 1"

    solar_circuit_current_temperature_2_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_1",
    )
    assert isinstance(solar_circuit_current_temperature_2_1, State)
    assert solar_circuit_current_temperature_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Ist-Temperatur 2"

    solar_circuit_current_temperature_2_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_2",
    )
    assert isinstance(solar_circuit_current_temperature_2_2, State)
    assert solar_circuit_current_temperature_2_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Ist-Temperatur 2"

    solar_circuit_target_temperature_1_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_1_1",
    )
    assert isinstance(solar_circuit_target_temperature_1_1, State)
    assert solar_circuit_target_temperature_1_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Soll-Temperatur 1"

    solar_circuit_target_temperature_1_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_1_2",
    )
    assert isinstance(solar_circuit_target_temperature_1_2, State)
    assert solar_circuit_target_temperature_1_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Soll-Temperatur 1"

    solar_circuit_target_temperature_2_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_2_1",
    )
    assert isinstance(solar_circuit_target_temperature_2_1, State)
    assert solar_circuit_target_temperature_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Soll-Temperatur 2"

    solar_circuit_target_temperature_2_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_target_temperature_2_2",
    )
    assert isinstance(solar_circuit_target_temperature_2_2, State)
    assert solar_circuit_target_temperature_2_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Soll-Temperatur 2"

    solar_circuit_heating_energy_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_heating_energy_1",
    )
    assert isinstance(solar_circuit_heating_energy_1, State)
    assert solar_circuit_heating_energy_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Wärmemenge"

    solar_circuit_heating_energy_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_heating_energy_2",
    )
    assert isinstance(solar_circuit_heating_energy_2, State)
    assert solar_circuit_heating_energy_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Wärmemenge"

    solar_circuit_daily_energy_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_daily_energy_1",
    )
    assert isinstance(solar_circuit_daily_energy_1, State)
    assert solar_circuit_daily_energy_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Tagesenergie"

    solar_circuit_daily_energy_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_daily_energy_2",
    )
    assert isinstance(solar_circuit_daily_energy_2, State)
    assert solar_circuit_daily_energy_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Tagesenergie"

    solar_circuit_actual_power_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_actual_power_1",
    )
    assert isinstance(solar_circuit_actual_power_1, State)
    assert solar_circuit_actual_power_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Leistung"

    solar_circuit_actual_power_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_solar_circuit_actual_power_2",
    )
    assert isinstance(solar_circuit_actual_power_2, State)
    assert solar_circuit_actual_power_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Leistung"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_external_heat_source_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    external_heat_source_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_operating_mode_1",
    )
    assert isinstance(external_heat_source_operating_mode_1, State)
    assert external_heat_source_operating_mode_1.state == "off"
    assert external_heat_source_operating_mode_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert external_heat_source_operating_mode_1.attributes[ATTR_OPTIONS] == [
        "off",
        "on",
    ]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_external_heat_source.state.{opt}"]
        for opt in external_heat_source_operating_mode_1.attributes[ATTR_OPTIONS]
    } == {
        "off": "Off",
        "on": "On",
    }
    assert (
        external_heat_source_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "External heat source 1 Operating mode"
    )

    external_heat_source_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_target_temperature_1",
    )
    assert isinstance(external_heat_source_target_temperature_1, State)
    assert external_heat_source_target_temperature_1.state == "17.23"
    assert external_heat_source_target_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert external_heat_source_target_temperature_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert external_heat_source_target_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        external_heat_source_target_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "External heat source 1 Target temperature"
    )

    external_heat_source_operating_time_2: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_operating_time_2",
    )
    assert isinstance(external_heat_source_operating_time_2, State)
    assert external_heat_source_operating_time_2.state == "225.83"
    assert external_heat_source_operating_time_2.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTime.HOURS
    assert external_heat_source_operating_time_2.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.DURATION
    assert external_heat_source_operating_time_2.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert (
        external_heat_source_operating_time_2.attributes[ATTR_FRIENDLY_NAME] == "External heat source 2 Operating time"
    )

    external_heat_source_max_runtime_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_max_runtime_1",
    )
    assert isinstance(external_heat_source_max_runtime_1, State)
    assert external_heat_source_max_runtime_1.state == "2.26"
    assert external_heat_source_max_runtime_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTime.HOURS
    assert external_heat_source_max_runtime_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert external_heat_source_max_runtime_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.DURATION
    assert external_heat_source_max_runtime_1.attributes[ATTR_FRIENDLY_NAME] == "External heat source 1 Maximum runtime"

    external_heat_source_activation_counter_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_activation_counter_1",
    )
    assert isinstance(external_heat_source_activation_counter_1, State)
    assert external_heat_source_activation_counter_1.state == "812"
    assert external_heat_source_activation_counter_1.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL_INCREASING
    assert (
        external_heat_source_activation_counter_1.attributes[ATTR_FRIENDLY_NAME]
        == "External heat source 1 Activation counter"
    )


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_external_heat_source_sensors_translated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    external_heat_source_operating_mode_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_operating_mode_1",
    )
    assert isinstance(external_heat_source_operating_mode_1, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.operating_mode_external_heat_source.state.{opt}"]
        for opt in external_heat_source_operating_mode_1.attributes[ATTR_OPTIONS]
    } == {
        "off": "Aus",
        "on": "Ein",
    }
    assert external_heat_source_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Externe Wärmequelle 1 Betriebsart"

    external_heat_source_target_temperature_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_target_temperature_1",
    )
    assert isinstance(external_heat_source_target_temperature_1, State)
    assert (
        external_heat_source_target_temperature_1.attributes[ATTR_FRIENDLY_NAME]
        == "Externe Wärmequelle 1 Soll-Temperatur"
    )

    external_heat_source_operating_time_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_operating_time_1",
    )
    assert isinstance(external_heat_source_operating_time_1, State)
    assert (
        external_heat_source_operating_time_1.attributes[ATTR_FRIENDLY_NAME] == "Externe Wärmequelle 1 Betriebsstunden"
    )

    external_heat_source_max_runtime_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_max_runtime_1",
    )
    assert isinstance(external_heat_source_max_runtime_1, State)
    assert (
        external_heat_source_max_runtime_1.attributes[ATTR_FRIENDLY_NAME] == "Externe Wärmequelle 1 Maximale Laufzeit"
    )

    external_heat_source_activation_counter_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_external_heat_source_activation_counter_1",
    )
    assert isinstance(external_heat_source_activation_counter_1, State)
    assert (
        external_heat_source_activation_counter_1.attributes[ATTR_FRIENDLY_NAME]
        == "Externe Wärmequelle 1 Einschaltvorgänge"
    )


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_switch_valve_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    switch_valve_position_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_switch_valve_position_1",
    )
    assert isinstance(switch_valve_position_1, State)
    assert switch_valve_position_1.state == "neutral"
    assert switch_valve_position_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENUM
    assert switch_valve_position_1.attributes[ATTR_OPTIONS] == [
        "neutral",
        "open",
        "closed",
    ]
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.switch_valve_position.state.{opt}"]
        for opt in switch_valve_position_1.attributes[ATTR_OPTIONS]
    } == {
        "closed": "Position 2",
        "neutral": "Neutral",
        "open": "Position 1",
    }
    assert switch_valve_position_1.attributes[ATTR_FRIENDLY_NAME] == "Switch valve 1 Position"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_switch_valve_sensors_translated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

    switch_valve_position_1: State | None = hass.states.get(
        "sensor.keba_keenergy_12345678_switch_valve_position_1",
    )
    assert isinstance(switch_valve_position_1, State)
    assert {
        opt: translations[f"component.keba_keenergy.entity.sensor.switch_valve_position.state.{opt}"]
        for opt in switch_valve_position_1.attributes[ATTR_OPTIONS]
    } == {
        "closed": "Position 2",
        "neutral": "Neutral",
        "open": "Position 1",
    }
    assert switch_valve_position_1.attributes[ATTR_FRIENDLY_NAME] == "Umschaltventil 1 Position"


# @pytest.mark.usefixtures("entity_registry_enabled_by_default")
# async def test_photovoltaic_sensors(
#     hass: HomeAssistant,
#     config_entry: MockConfigEntry,
#     fake_api: FakeKebaKeEnergyAPI,
# ) -> None:
#     """Test external heat source sensors."""
#     fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
#     fake_api.register_requests(config_entry.data[CONF_HOST])
#
#     await setup_integration(hass, config_entry)
#
#     photovoltaic_excess_power: State | None = hass.states.get(
#         "sensor.keba_keenergy_12345678_photovoltaic_excess_power",
#     )
#     assert isinstance(photovoltaic_excess_power, State)
#     assert photovoltaic_excess_power.state == "437.7"
#     assert photovoltaic_excess_power.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfPower.WATT
#     assert photovoltaic_excess_power.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
#     assert photovoltaic_excess_power.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.POWER
#     assert photovoltaic_excess_power.attributes[ATTR_FRIENDLY_NAME] == "Photovoltaic Excess power"
#
#     photovoltaic_daily_energy: State | None = hass.states.get(
#         "sensor.keba_keenergy_12345678_photovoltaic_daily_energy",
#     )
#     assert isinstance(photovoltaic_daily_energy, State)
#     assert photovoltaic_daily_energy.state == "437.7"
#     assert photovoltaic_daily_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
#     assert photovoltaic_daily_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
#     assert photovoltaic_daily_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
#     assert photovoltaic_daily_energy.attributes[ATTR_FRIENDLY_NAME] == "Photovoltaic Daily energy"
#
#     photovoltaic_total_energy: State | None = hass.states.get(
#         "sensor.keba_keenergy_12345678_photovoltaic_total_energy",
#     )
#     assert isinstance(photovoltaic_total_energy, State)
#     assert photovoltaic_total_energy.state == "437.7"
#     assert photovoltaic_total_energy.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfEnergy.KILO_WATT_HOUR
#     assert photovoltaic_total_energy.attributes[ATTR_STATE_CLASS] == SensorStateClass.TOTAL
#     assert photovoltaic_total_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
#     assert photovoltaic_total_energy.attributes[ATTR_FRIENDLY_NAME] == "Photovoltaic Total energy"
#
#
# @pytest.mark.usefixtures("entity_registry_enabled_by_default")
# async def test_photovoltaic_sensors_translated(
#     hass: HomeAssistant,
#     config_entry: MockConfigEntry,
#     fake_api: FakeKebaKeEnergyAPI,
# ) -> None:
#     """Test photovoltaic sensors translations."""
#     fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
#     fake_api.register_requests(config_entry.data[CONF_HOST])
#
#     hass.config.language = "de"
#     await setup_integration(hass, config_entry)
#
#     photovoltaic_excess_power: State | None = hass.states.get(
#         "sensor.keba_keenergy_12345678_photovoltaic_excess_power",
#     )
#     assert isinstance(photovoltaic_excess_power, State)
#     assert photovoltaic_excess_power.attributes[ATTR_FRIENDLY_NAME] == "Photovoltaik Überschussleistung"
#
#     photovoltaic_daily_energy: State | None = hass.states.get(
#         "sensor.keba_keenergy_12345678_photovoltaic_daily_energy",
#     )
#     assert isinstance(photovoltaic_daily_energy, State)
#     assert photovoltaic_daily_energy.attributes[ATTR_FRIENDLY_NAME] == "Photovoltaik Tagesenergie"
#
#     photovoltaic_total_energy: State | None = hass.states.get(
#         "sensor.keba_keenergy_12345678_photovoltaic_total_energy",
#     )
#     assert isinstance(photovoltaic_total_energy, State)
#     assert photovoltaic_total_energy.state == "437.7"
#     assert photovoltaic_total_energy.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.ENERGY
#     assert photovoltaic_total_energy.attributes[ATTR_FRIENDLY_NAME] == "Photovoltaik Gesamtenergie"
