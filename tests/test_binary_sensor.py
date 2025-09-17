from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.const import CONF_HOST
from homeassistant.const import STATE_OFF
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.conftest import FakeKebaKeEnergyAPI


async def test_binary_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test binary sensors."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

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

    heat_pump_heat_request: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_heat_request",
    )
    assert isinstance(heat_pump_heat_request, State)
    assert heat_pump_heat_request.state == STATE_OFF
    assert heat_pump_heat_request.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Heat request"


async def test_binary_sensors_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test binary sensors."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

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

    heat_pump_heat_request: State | None = hass.states.get(
        "binary_sensor.keba_keenergy_12345678_heat_pump_heat_request",
    )
    assert isinstance(heat_pump_heat_request, State)
    assert heat_pump_heat_request.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Heizanforderung"
