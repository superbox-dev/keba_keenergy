import pytest
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.components.switch.const import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.const import CONF_DEVICE_CLASS
from homeassistant.const import CONF_HOST
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multi_positions_data_response
from tests.conftest import FakeKebaKeEnergyAPI


async def test_solar_circuit_switches(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test solar circuit switches."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    solar_circuit_priority_1_before_2_1: State | None = hass.states.get(
        "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_1",
    )
    assert isinstance(solar_circuit_priority_1_before_2_1, State)
    assert solar_circuit_priority_1_before_2_1.attributes[CONF_DEVICE_CLASS] == SwitchDeviceClass.SWITCH
    assert solar_circuit_priority_1_before_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Priority 1 before 2"


async def test_solar_circuit_switches_translated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test solar circuit switches translated."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    solar_circuit_priority_1_before_2_1: State | None = hass.states.get(
        "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_1",
    )
    assert solar_circuit_priority_1_before_2_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Vorrang 1 vor 2"


async def test_heat_pump_switches(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test heat pump switches."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    heat_pump_compressor_use_night_speed: State | None = hass.states.get(
        "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed",
    )
    assert isinstance(heat_pump_compressor_use_night_speed, State)
    assert heat_pump_compressor_use_night_speed.attributes[CONF_DEVICE_CLASS] == SwitchDeviceClass.SWITCH
    assert (
        heat_pump_compressor_use_night_speed.attributes[ATTR_FRIENDLY_NAME]
        == "Heat pump Compressor speed limit (night)"
    )


async def test_heat_pump_switches_translated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test heat pump switches translated."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    heat_pump_compressor_use_night_speed: State | None = hass.states.get(
        "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed",
    )
    assert (
        heat_pump_compressor_use_night_speed.attributes[ATTR_FRIENDLY_NAME]
        == "Wärmepumpe Kompressor-Drehzahlbegrenzung (Nacht)"
    )


@pytest.mark.parametrize(
    ("entity_id", "service", "expected"),
    [
        (
            "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed",
            SERVICE_TURN_ON,
            '[{"name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed", "value": "1"}]',
        ),
        (
            "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed",
            SERVICE_TURN_OFF,
            '[{"name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed", "value": "0"}]',
        ),
        (
            "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_2",
            SERVICE_TURN_ON,
            '[{"name": "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]", "value": "1"}, '
            '{"name": "APPL.CtrlAppl.sParam.genericHeat[2].param.priority", "value": "14"}]',
        ),
        (
            "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_2",
            SERVICE_TURN_OFF,
            '[{"name": "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]", "value": "0"}, '
            '{"name": "APPL.CtrlAppl.sParam.genericHeat[2].param.priority", "value": "15"}]',
        ),
    ],
)
async def test_set_value(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    service: str,
    expected: str,
) -> None:
    """Test set the value."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    await hass.services.async_call(
        domain=SWITCH_DOMAIN,
        service=service,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)
