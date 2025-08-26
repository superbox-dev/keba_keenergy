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
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from keba_keenergy_api.constants import HotWaterTankOperatingMode
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import DEFAULT_POSITION_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.conftest import FakeKebaKeEnergyAPI

ENTITY_ID: str = "water_heater.keba_keenergy_12345678"
ENTITY_ID_1: str = "water_heater.keba_keenergy_12345678_1"
ENTITY_ID_2: str = "water_heater.keba_keenergy_12345678_2"


@pytest.mark.parametrize(
    ("response", "entities"),
    [
        ([DEFAULT_POSITION_RESPONSE, DEFAULT_POSITION_DATA_RESPONSE], [ENTITY_ID]),
        ([MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE], [ENTITY_ID_1, ENTITY_ID_2]),
    ],
)
async def test_water_heater_entities(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    response: list[list[dict[str, Any]]],
    entities: list[str],
) -> None:
    """Test water heater entities."""
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
    """Test water heater."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    state: State | None = hass.states.get(ENTITY_ID_1)
    assert isinstance(state, State)

    assert state.attributes[ATTR_CURRENT_TEMPERATURE] == 47.7
    assert state.attributes[ATTR_MIN_TEMP] == 0.0
    assert state.attributes[ATTR_MAX_TEMP] == 52.0
    assert state.attributes[ATTR_OPERATION_MODE] == STATE_PERFORMANCE
    assert state.attributes[ATTR_TEMPERATURE] == 51.0
    assert state.attributes[ATTR_TARGET_TEMP_LOW] == 32.5
    assert state.attributes[ATTR_TARGET_TEMP_HIGH] == 52.0


async def test_turn_off(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test turn on water heater."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_TURN_OFF,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        f'[{{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", '
        f'"value": "{HotWaterTankOperatingMode.OFF.value}"}}]',
    )


async def test_turn_on(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test turn on water heater."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_TURN_ON,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        f'[{{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", '
        f'"value": "{HotWaterTankOperatingMode.ON.value}"}}]',
    )


@pytest.mark.parametrize(
    ("operation_mode", "expected_operating_mode"),
    [
        (STATE_ECO, HotWaterTankOperatingMode.AUTO.value),
        (STATE_PERFORMANCE, HotWaterTankOperatingMode.HEAT_UP.value),
        (STATE_OFF, HotWaterTankOperatingMode.OFF.value),
        (STATE_HEAT_PUMP, HotWaterTankOperatingMode.ON.value),
    ],
)
async def test_set_operation_mode(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    operation_mode: str,
    expected_operating_mode: str,
) -> None:
    """Test set operation mode."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_OPERATION_MODE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
            ATTR_OPERATION_MODE: operation_mode,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        f'[{{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", '
        f'"value": "{expected_operating_mode}"}}]',
    )


async def test_set_temperature(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test setting temperature."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
            ATTR_TEMPERATURE: 45,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", "value": "45.0"}]',
    )
