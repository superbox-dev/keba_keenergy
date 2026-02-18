import pytest
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.const import CONF_HOST
from homeassistant.const import STATE_OFF
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_binary_sensors(
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

    solar_circuit_heat_request_1_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_1",
    )
    assert isinstance(solar_circuit_heat_request_1_1, State)
    assert solar_circuit_heat_request_1_1.state == STATE_ON
    assert solar_circuit_heat_request_1_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Heat request 1"

    solar_circuit_heat_request_1_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_2",
    )
    assert isinstance(solar_circuit_heat_request_1_2, State)
    assert solar_circuit_heat_request_1_2.state == STATE_OFF
    assert solar_circuit_heat_request_1_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Heat request 1"

    solar_circuit_heat_request_2_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_1",
    )
    assert isinstance(solar_circuit_heat_request_2_1, State)
    assert solar_circuit_heat_request_2_1.state == STATE_OFF
    assert solar_circuit_heat_request_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Heat request 2"

    solar_circuit_heat_request_2_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_2",
    )
    assert isinstance(solar_circuit_heat_request_2_2, State)
    assert solar_circuit_heat_request_2_2.state == STATE_ON
    assert solar_circuit_heat_request_2_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Heat request 2"

    buffer_tank_heat_request_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_buffer_tank_heat_request_1",
    )
    assert isinstance(buffer_tank_heat_request_1, State)
    assert buffer_tank_heat_request_1.state == STATE_OFF
    assert buffer_tank_heat_request_1.attributes[ATTR_FRIENDLY_NAME] == "Buffer tank 1 Heat request"

    buffer_tank_cool_request_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_buffer_tank_cool_request_1",
    )
    assert isinstance(buffer_tank_cool_request_1, State)
    assert buffer_tank_cool_request_1.state == STATE_ON
    assert buffer_tank_cool_request_1.attributes[ATTR_FRIENDLY_NAME] == "Buffer tank 1 Cool request"

    hot_water_tank_heat_request_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_heat_request_1",
    )
    assert isinstance(hot_water_tank_heat_request_1, State)
    assert hot_water_tank_heat_request_1.state == STATE_OFF
    assert hot_water_tank_heat_request_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 1 Heat request"

    hot_water_tank_heat_request_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_heat_request_2",
    )
    assert isinstance(hot_water_tank_heat_request_2, State)
    assert hot_water_tank_heat_request_2.state == STATE_ON
    assert hot_water_tank_heat_request_2.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 2 Heat request"

    hot_water_tank_hot_water_flow_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_hot_water_flow_1",
    )
    assert isinstance(hot_water_tank_hot_water_flow_1, State)
    assert hot_water_tank_hot_water_flow_1.state == STATE_OFF
    assert hot_water_tank_hot_water_flow_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 1 Hot water flow"

    hot_water_tank_hot_water_flow_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_hot_water_flow_2",
    )
    assert isinstance(hot_water_tank_hot_water_flow_2, State)
    assert hot_water_tank_hot_water_flow_2.state == STATE_ON
    assert hot_water_tank_hot_water_flow_2.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 2 Hot water flow"

    hot_water_tank_circulation_pump_state_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_circulation_pump_state_1",
    )
    assert isinstance(hot_water_tank_circulation_pump_state_1, State)
    assert hot_water_tank_circulation_pump_state_1.state == STATE_ON
    assert (
        hot_water_tank_circulation_pump_state_1.attributes[ATTR_FRIENDLY_NAME]
        == "Hot water tank 1 Circulation pump state"
    )

    hot_water_tank_circulation_pump_state_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_circulation_pump_state_2",
    )
    assert isinstance(hot_water_tank_circulation_pump_state_2, State)
    assert hot_water_tank_circulation_pump_state_2.state == STATE_OFF
    assert (
        hot_water_tank_circulation_pump_state_2.attributes[ATTR_FRIENDLY_NAME]
        == "Hot water tank 2 Circulation pump state"
    )

    heat_pump_heat_request: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_heat_request",
    )
    assert isinstance(heat_pump_heat_request, State)
    assert heat_pump_heat_request.state == STATE_OFF
    assert heat_pump_heat_request.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heat request"

    heat_pump_has_compressor_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_compressor_failure",
    )
    assert isinstance(heat_pump_has_compressor_failure, State)
    assert heat_pump_has_compressor_failure.state == STATE_OFF
    assert heat_pump_has_compressor_failure.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Compressor"

    heat_pump_has_source_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_failure",
    )
    assert isinstance(heat_pump_has_source_failure, State)
    assert heat_pump_has_source_failure.state == STATE_OFF
    assert heat_pump_has_source_failure.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Source"

    heat_pump_has_source_actuator_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_actuator_failure",
    )
    assert isinstance(heat_pump_has_source_actuator_failure, State)
    assert heat_pump_has_source_actuator_failure.state == STATE_OFF
    assert heat_pump_has_source_actuator_failure.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Source actuator"

    heat_pump_has_three_phase_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_three_phase_failure",
    )
    assert isinstance(heat_pump_has_three_phase_failure, State)
    assert heat_pump_has_three_phase_failure.state == STATE_OFF
    assert heat_pump_has_three_phase_failure.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Three-phase"

    heat_pump_has_source_pressure_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_pressure_failure",
    )
    assert isinstance(heat_pump_has_source_pressure_failure, State)
    assert heat_pump_has_source_pressure_failure.state == STATE_OFF
    assert heat_pump_has_source_pressure_failure.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Source pressure"

    heat_pump_has_vfd_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_vfd_failure",
    )
    assert isinstance(heat_pump_has_vfd_failure, State)
    assert heat_pump_has_vfd_failure.state == STATE_OFF
    assert heat_pump_has_vfd_failure.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Variable drive frequency"

    external_heat_source_heat_request_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_external_heat_source_heat_request_1",
    )
    assert isinstance(external_heat_source_heat_request_1, State)
    assert external_heat_source_heat_request_1.state == STATE_ON
    assert external_heat_source_heat_request_1.attributes[ATTR_FRIENDLY_NAME] == "External heat source 1 Heat request"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_binary_sensors_translations(
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

    solar_circuit_heat_request_1_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_1",
    )
    assert isinstance(solar_circuit_heat_request_1_1, State)
    assert solar_circuit_heat_request_1_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Heizanforderung 1"

    solar_circuit_heat_request_1_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_1_2",
    )
    assert isinstance(solar_circuit_heat_request_1_2, State)
    assert solar_circuit_heat_request_1_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Heizanforderung 1"

    solar_circuit_heat_request_2_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_1",
    )
    assert isinstance(solar_circuit_heat_request_2_1, State)
    assert solar_circuit_heat_request_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Heizanforderung 2"

    solar_circuit_heat_request_2_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_solar_circuit_heat_request_2_2",
    )
    assert isinstance(solar_circuit_heat_request_2_2, State)
    assert solar_circuit_heat_request_2_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Heizanforderung 2"

    buffer_tank_heat_request_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_buffer_tank_heat_request_1",
    )
    assert isinstance(buffer_tank_heat_request_1, State)
    assert buffer_tank_heat_request_1.attributes[ATTR_FRIENDLY_NAME] == "Pufferspeicher 1 Heizanforderung"

    buffer_tank_cool_request_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_buffer_tank_cool_request_1",
    )
    assert isinstance(buffer_tank_cool_request_1, State)
    assert buffer_tank_cool_request_1.attributes[ATTR_FRIENDLY_NAME] == "Pufferspeicher 1 Kühlanforderung"

    hot_water_tank_heat_request_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_heat_request_1",
    )
    assert isinstance(hot_water_tank_heat_request_1, State)
    assert hot_water_tank_heat_request_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 1 Heizanforderung"

    hot_water_tank_heat_request_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_heat_request_2",
    )
    assert isinstance(hot_water_tank_heat_request_2, State)
    assert hot_water_tank_heat_request_2.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 2 Heizanforderung"

    hot_water_tank_hot_water_flow_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_hot_water_flow_1",
    )
    assert isinstance(hot_water_tank_hot_water_flow_1, State)
    assert hot_water_tank_hot_water_flow_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 1 Warmwasser läuft"

    hot_water_tank_hot_water_flow_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_hot_water_flow_2",
    )
    assert isinstance(hot_water_tank_hot_water_flow_2, State)
    assert hot_water_tank_hot_water_flow_2.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 2 Warmwasser läuft"

    hot_water_tank_circulation_pump_state_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_circulation_pump_state_1",
    )
    assert isinstance(hot_water_tank_circulation_pump_state_1, State)
    assert (
        hot_water_tank_circulation_pump_state_1.attributes[ATTR_FRIENDLY_NAME]
        == "Warmwasserspeicher 1 Zirkulationspumpe Status"
    )

    hot_water_tank_circulation_pump_state_2: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_hot_water_tank_circulation_pump_state_2",
    )
    assert isinstance(hot_water_tank_circulation_pump_state_2, State)
    assert (
        hot_water_tank_circulation_pump_state_2.attributes[ATTR_FRIENDLY_NAME]
        == "Warmwasserspeicher 2 Zirkulationspumpe Status"
    )

    heat_pump_heat_request: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_heat_request",
    )
    assert isinstance(heat_pump_heat_request, State)
    assert heat_pump_heat_request.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Heizanforderung"

    heat_pump_has_compressor_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_compressor_failure",
    )
    assert isinstance(heat_pump_has_compressor_failure, State)
    assert heat_pump_has_compressor_failure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Kompressor"

    heat_pump_has_source_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_failure",
    )
    assert isinstance(heat_pump_has_source_failure, State)
    assert heat_pump_has_source_failure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Quelle"

    heat_pump_has_source_actuator_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_actuator_failure",
    )
    assert isinstance(heat_pump_has_source_actuator_failure, State)
    assert heat_pump_has_source_actuator_failure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Quellenaktor"

    heat_pump_has_three_phase_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_three_phase_failure",
    )
    assert isinstance(heat_pump_has_three_phase_failure, State)
    assert heat_pump_has_three_phase_failure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe 3-Phase"

    heat_pump_has_source_pressure_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_source_pressure_failure",
    )
    assert isinstance(heat_pump_has_source_pressure_failure, State)
    assert heat_pump_has_source_pressure_failure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Quellendruck"

    heat_pump_has_vfd_failure: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_has_vfd_failure",
    )
    assert isinstance(heat_pump_has_vfd_failure, State)
    assert heat_pump_has_vfd_failure.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Frequenzumrichter"

    external_heat_source_heat_request_1: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_external_heat_source_heat_request_1",
    )
    assert isinstance(external_heat_source_heat_request_1, State)
    assert external_heat_source_heat_request_1.attributes[ATTR_FRIENDLY_NAME] == "Externe Wärmequelle 1 Heizanforderung"
