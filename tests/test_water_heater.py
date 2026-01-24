from typing import Any

import pytest
from homeassistant.components.water_heater import ATTR_CURRENT_TEMPERATURE
from homeassistant.components.water_heater import ATTR_MAX_TEMP
from homeassistant.components.water_heater import ATTR_MIN_TEMP
from homeassistant.components.water_heater import ATTR_OPERATION_MODE
from homeassistant.components.water_heater import ATTR_TARGET_TEMP_HIGH
from homeassistant.components.water_heater import ATTR_TARGET_TEMP_LOW
from homeassistant.components.water_heater import SERVICE_SET_OPERATION_MODE
from homeassistant.components.water_heater import SERVICE_SET_TEMPERATURE
from homeassistant.components.water_heater.const import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.components.water_heater.const import STATE_ECO
from homeassistant.components.water_heater.const import STATE_HEAT_PUMP
from homeassistant.components.water_heater.const import STATE_PERFORMANCE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import DEFAULT_POSITION_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_FIXED_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI

ENTITY_ID: str = "water_heater.keba_keenergy_12345678"
ENTITY_ID_1: str = "water_heater.keba_keenergy_12345678_1"
ENTITY_ID_2: str = "water_heater.keba_keenergy_12345678_2"
ENTITY_ID_3: str = "water_heater.keba_keenergy_12345678_buffer_tank"
ENTITY_ID_4: str = "water_heater.keba_keenergy_12345678_buffer_tank_1"


@pytest.mark.parametrize(
    ("response", "entities"),
    [
        (
            [DEFAULT_POSITION_RESPONSE, DEFAULT_POSITION_FIXED_DATA_RESPONSE, DEFAULT_POSITION_DATA_RESPONSE],
            [ENTITY_ID, ENTITY_ID_3],
        ),
        (
            [
                MULTIPLE_POSITIONS_RESPONSE,
                get_multiple_position_fixed_data_response(),
                MULTIPLE_POSITIONS_DATA_RESPONSE_1,
            ],
            [ENTITY_ID_1, ENTITY_ID_2, ENTITY_ID_4],
        ),
    ],
)
async def test_water_heater_entities(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    response: list[list[dict[str, Any]]],
    entities: list[str],
) -> None:
    fake_api.responses = response
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    for entity in entities:
        assert isinstance(hass.states.get(entity), State)


async def test_water_heater(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    keba_keenergy_12345678_1: State | None = hass.states.get("water_heater.keba_keenergy_12345678_1")
    assert isinstance(keba_keenergy_12345678_1, State)

    assert keba_keenergy_12345678_1.attributes[ATTR_CURRENT_TEMPERATURE] == 47.7
    assert keba_keenergy_12345678_1.attributes[ATTR_MIN_TEMP] == 0.0
    assert keba_keenergy_12345678_1.attributes[ATTR_MAX_TEMP] == 52.0
    assert keba_keenergy_12345678_1.attributes[ATTR_OPERATION_MODE] == STATE_PERFORMANCE
    assert keba_keenergy_12345678_1.attributes[ATTR_TEMPERATURE] == 51.0
    assert keba_keenergy_12345678_1.attributes[ATTR_TARGET_TEMP_LOW] == 32.5
    assert keba_keenergy_12345678_1.attributes[ATTR_TARGET_TEMP_HIGH] == 51.0
    assert keba_keenergy_12345678_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 1"

    keba_keenergy_12345678_buffer_tank_1: State | None = hass.states.get(
        "water_heater.keba_keenergy_12345678_buffer_tank_1",
    )
    assert isinstance(keba_keenergy_12345678_buffer_tank_1, State)

    assert keba_keenergy_12345678_buffer_tank_1.attributes[ATTR_CURRENT_TEMPERATURE] == 45.7
    assert keba_keenergy_12345678_buffer_tank_1.attributes[ATTR_OPERATION_MODE] == STATE_OFF
    assert keba_keenergy_12345678_buffer_tank_1.attributes[ATTR_TEMPERATURE] == 44.0
    assert keba_keenergy_12345678_buffer_tank_1.attributes[ATTR_TARGET_TEMP_LOW] == 10.0
    assert keba_keenergy_12345678_buffer_tank_1.attributes[ATTR_TARGET_TEMP_HIGH] == 44.0
    assert keba_keenergy_12345678_buffer_tank_1.attributes[ATTR_FRIENDLY_NAME] == "Buffer tank 1"


async def test_water_heater_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
    ]
    fake_api.register_requests("10.0.0.100")

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    keba_keenergy_12345678_1: State | None = hass.states.get("water_heater.keba_keenergy_12345678_1")
    assert isinstance(keba_keenergy_12345678_1, State)
    assert keba_keenergy_12345678_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 1"

    keba_keenergy_12345678_buffer_tank_1: State | None = hass.states.get(
        "water_heater.keba_keenergy_12345678_buffer_tank_1",
    )
    assert isinstance(keba_keenergy_12345678_buffer_tank_1, State)
    assert keba_keenergy_12345678_buffer_tank_1.attributes[ATTR_FRIENDLY_NAME] == "Pufferspeicher 1"


@pytest.mark.parametrize(
    ("entity_id", "expected"),
    [
        (
            "water_heater.keba_keenergy_12345678_1",
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "0"}]',
        ),
        (
            "water_heater.keba_keenergy_12345678_buffer_tank_1",
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "0"}]',
        ),
    ],
)
async def test_turn_off(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
    ]
    fake_api.register_requests("10.0.0.100")

    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_TURN_OFF,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("entity_id", "expected"),
    [
        (
            "water_heater.keba_keenergy_12345678_1",
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "2"}]',
        ),
        (
            "water_heater.keba_keenergy_12345678_buffer_tank_1",
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "1"}]',
        ),
    ],
)
async def test_turn_on(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
    ]
    fake_api.register_requests("10.0.0.100")

    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_TURN_ON,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("entity_id", "operation_mode", "expected"),
    [
        (
            "water_heater.keba_keenergy_12345678_1",
            STATE_ECO,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "1"}]',
        ),
        (
            "water_heater.keba_keenergy_12345678_1",
            STATE_PERFORMANCE,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "3"}]',
        ),
        (
            "water_heater.keba_keenergy_12345678_1",
            STATE_OFF,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "0"}]',
        ),
        (
            "water_heater.keba_keenergy_12345678_1",
            STATE_HEAT_PUMP,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "2"}]',
        ),
        (
            "water_heater.keba_keenergy_12345678_buffer_tank_1",
            STATE_PERFORMANCE,
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "2"}]',
        ),
        (
            "water_heater.keba_keenergy_12345678_buffer_tank_1",
            STATE_OFF,
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "0"}]',
        ),
        (
            "water_heater.keba_keenergy_12345678_buffer_tank_1",
            STATE_HEAT_PUMP,
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "1"}]',
        ),
    ],
)
async def test_set_operation_mode(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    operation_mode: str,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_OPERATION_MODE,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_OPERATION_MODE: operation_mode,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("entity_id", "value", "expected"),
    [
        (
            "water_heater.keba_keenergy_12345678_1",
            45,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", "value": "45.0"}]',
        ),
    ],
)
async def test_set_temperature(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: int,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_TEMPERATURE: value,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)
