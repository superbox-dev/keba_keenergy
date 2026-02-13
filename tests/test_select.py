from typing import Any

import pytest
from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    ("response", "expected_attr_options"),
    [
        (
            [
                MULTIPLE_POSITIONS_RESPONSE,
                get_multiple_position_fixed_data_response(has_passive_cooling="true"),
                MULTIPLE_POSITION_DATA_RESPONSE_1,
                HEATING_CURVES_RESPONSE_1_1,
            ],
            ["standby", "summer", "auto_heat", "auto_cool", "auto"],
        ),
        (
            [
                MULTIPLE_POSITIONS_RESPONSE,
                get_multiple_position_fixed_data_response(has_passive_cooling="false"),
                MULTIPLE_POSITION_DATA_RESPONSE_1,
                HEATING_CURVES_RESPONSE_1_1,
            ],
            ["standby", "summer", "auto_heat"],
        ),
    ],
)
async def test_system_selects(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    response: list[list[dict[str, Any]]],
    expected_attr_options: list[str],
) -> None:
    fake_api.responses = response
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    operating_mode: State | None = hass.states.get("select.keba_keenergy_12345678_operating_mode")
    assert isinstance(operating_mode, State)
    assert operating_mode.state == "auto_heat"
    assert operating_mode.attributes[ATTR_FRIENDLY_NAME] == "Control unit Operating mode"
    assert operating_mode.attributes[ATTR_OPTIONS] == expected_attr_options


async def test_system_selects_translations(
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

    operating_mode: State | None = hass.states.get("select.keba_keenergy_12345678_operating_mode")
    assert isinstance(operating_mode, State)
    assert operating_mode.attributes[ATTR_FRIENDLY_NAME] == "Bedieneinheit Betriebsart"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_circuit_selects(
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

    heat_circuit_operating_mode_1: State | None = hass.states.get(
        "select.keba_keenergy_12345678_heat_circuit_operating_mode_1",
    )
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.state == "day"
    assert heat_circuit_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Operating mode"
    assert heat_circuit_operating_mode_1.attributes[ATTR_OPTIONS] == ["off", "auto", "day", "night", "holiday", "party"]

    heat_circuit_heating_curve_1: State | None = hass.states.get(
        "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
    )
    assert isinstance(heat_circuit_heating_curve_1, State)
    assert heat_circuit_heating_curve_1.state == "HC6"
    assert heat_circuit_heating_curve_1.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 1 Heating curve"
    assert heat_circuit_heating_curve_1.attributes[ATTR_OPTIONS] == [
        "HC1",
        "HC2",
        "HC3",
        "HC4",
        "HC5",
        "HC6",
        "HC7",
        "HC8",
        "HC_FBH",
        "HC_HK",
    ]


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heat_circuit_selects_translated(
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

    heat_circuit_operating_mode_1: State | None = hass.states.get(
        "select.keba_keenergy_12345678_heat_circuit_operating_mode_1",
    )
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Betriebsart"

    heat_circuit_heating_curve_1: State | None = hass.states.get(
        "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
    )
    assert isinstance(heat_circuit_heating_curve_1, State)
    assert heat_circuit_heating_curve_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Heizkurve"


async def test_solar_circuit_selects(
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

    solar_circuit_operating_mode_1: State | None = hass.states.get(
        "select.keba_keenergy_12345678_solar_circuit_operating_mode_1",
    )
    assert isinstance(solar_circuit_operating_mode_1, State)
    assert solar_circuit_operating_mode_1.state == "off"
    assert solar_circuit_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 1 Operating mode"
    assert solar_circuit_operating_mode_1.attributes[ATTR_OPTIONS] == ["off", "on"]

    solar_circuit_operating_mode_2: State | None = hass.states.get(
        "select.keba_keenergy_12345678_solar_circuit_operating_mode_2",
    )
    assert isinstance(solar_circuit_operating_mode_2, State)
    assert solar_circuit_operating_mode_2.state == "on"
    assert solar_circuit_operating_mode_2.attributes[ATTR_FRIENDLY_NAME] == "Solar circuit 2 Operating mode"
    assert solar_circuit_operating_mode_2.attributes[ATTR_OPTIONS] == ["off", "on"]


async def test_solar_circuit_selects_translated(
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

    solar_circuit_operating_mode_1: State | None = hass.states.get(
        "select.keba_keenergy_12345678_solar_circuit_operating_mode_1",
    )
    assert isinstance(solar_circuit_operating_mode_1, State)
    assert solar_circuit_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 1 Betriebsart"

    solar_circuit_operating_mode_2: State | None = hass.states.get(
        "select.keba_keenergy_12345678_solar_circuit_operating_mode_2",
    )
    assert isinstance(solar_circuit_operating_mode_2, State)
    assert solar_circuit_operating_mode_2.attributes[ATTR_FRIENDLY_NAME] == "Solarkreis 2 Betriebsart"


async def test_buffer_tank_selects(
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

    buffer_tank_operating_mode_2: State | None = hass.states.get(
        "select.keba_keenergy_12345678_buffer_tank_operating_mode_2",
    )
    assert isinstance(buffer_tank_operating_mode_2, State)
    assert buffer_tank_operating_mode_2.state == "on"
    assert buffer_tank_operating_mode_2.attributes[ATTR_FRIENDLY_NAME] == "Buffer tank 2 Operating mode"
    assert buffer_tank_operating_mode_2.attributes[ATTR_OPTIONS] == [
        "off",
        "on",
        "heat_up",
    ]


async def test_buffer_tank_selects_translated(
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

    buffer_tank_operating_mode_2: State | None = hass.states.get(
        "select.keba_keenergy_12345678_buffer_tank_operating_mode_2",
    )
    assert isinstance(buffer_tank_operating_mode_2, State)
    assert buffer_tank_operating_mode_2.attributes[ATTR_FRIENDLY_NAME] == "Pufferspeicher 2 Betriebsart"


async def test_hot_water_tank_selects(
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

    hot_water_tank_operating_mode_2: State | None = hass.states.get(
        "select.keba_keenergy_12345678_hot_water_tank_operating_mode_2",
    )
    assert isinstance(hot_water_tank_operating_mode_2, State)
    assert hot_water_tank_operating_mode_2.state == "off"
    assert hot_water_tank_operating_mode_2.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 2 Operating mode"
    assert hot_water_tank_operating_mode_2.attributes[ATTR_OPTIONS] == [
        "off",
        "auto",
        "on",
        "heat_up",
    ]


async def test_hot_water_tank_selects_translated(
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

    hot_water_tank_operating_mode_2: State | None = hass.states.get(
        "select.keba_keenergy_12345678_hot_water_tank_operating_mode_2",
    )
    assert isinstance(hot_water_tank_operating_mode_2, State)
    assert hot_water_tank_operating_mode_2.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 2 Betriebsart"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_external_heat_source_selects(
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

    heat_source_operating_mode_1: State | None = hass.states.get(
        "select.keba_keenergy_12345678_external_heat_source_operating_mode_1",
    )
    assert isinstance(heat_source_operating_mode_1, State)
    assert heat_source_operating_mode_1.state == "off"
    assert heat_source_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "External heat source 1 Operating mode"
    assert heat_source_operating_mode_1.attributes[ATTR_OPTIONS] == [
        "off",
        "on",
    ]


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_external_heat_source_translated(
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

    external_heat_source_operating_mode_1: State | None = hass.states.get(
        "select.keba_keenergy_12345678_external_heat_source_operating_mode_1",
    )
    assert isinstance(external_heat_source_operating_mode_1, State)
    assert external_heat_source_operating_mode_1.attributes[ATTR_FRIENDLY_NAME] == "Externe Wärmequelle 1 Betriebsart"


@pytest.mark.parametrize(
    ("entity_id", "option", "expected"),
    [
        (
            "select.keba_keenergy_12345678_operating_mode",
            "auto_cool",
            '[{"name": "APPL.CtrlAppl.sParam.param.operatingMode", "value": "3"}]',
        ),
        (
            "select.keba_keenergy_12345678_heat_circuit_operating_mode_1",
            "off",
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode", "value": "0"}]',
        ),
        (
            "select.keba_keenergy_12345678_solar_circuit_operating_mode_1",
            "on",
            '[{"name": "APPL.CtrlAppl.sParam.solarCircuit[0].param.operatingMode", "value": "1"}]',
        ),
        (
            "select.keba_keenergy_12345678_hot_water_tank_operating_mode_2",
            "heat_up",
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[1].param.operatingMode", "value": "3"}]',
        ),
        (
            "select.keba_keenergy_12345678_external_heat_source_operating_mode_1",
            "on",
            '[{"name": "APPL.CtrlAppl.sParam.extHeatSource[0].param.operatingMode", "value": "1"}]',
        ),
        (
            "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
            "HC_FBH",
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.linTab.fileName", "value": "HC FBH"}]',
        ),
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_select_option(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    option: int,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_OPTION: option,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("entity_id", "option", "expected"),
    [
        (
            "select.keba_keenergy_12345678_operating_mode",
            "auto_cool",
            (
                "Option auto_cool is not valid for entity select.keba_keenergy_12345678_operating_mode, "
                "valid options are: standby, summer, auto_heat"
            ),
        ),
    ],
)
async def test_select_invalid_option(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    option: int,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="false"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    with pytest.raises(ServiceValidationError, match=expected):
        await hass.services.async_call(
            domain=SELECT_DOMAIN,
            service=SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_OPTION: option,
            },
            blocking=True,
        )
