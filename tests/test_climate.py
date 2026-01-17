from typing import Any

import pytest
from homeassistant.components.climate.const import ATTR_CURRENT_HUMIDITY
from homeassistant.components.climate.const import ATTR_CURRENT_TEMPERATURE
from homeassistant.components.climate.const import ATTR_HVAC_ACTION
from homeassistant.components.climate.const import ATTR_HVAC_MODE
from homeassistant.components.climate.const import ATTR_HVAC_MODES
from homeassistant.components.climate.const import ATTR_MAX_TEMP
from homeassistant.components.climate.const import ATTR_MIN_TEMP
from homeassistant.components.climate.const import ATTR_PRESET_MODE
from homeassistant.components.climate.const import ATTR_PRESET_MODES
from homeassistant.components.climate.const import ATTR_TARGET_TEMP_STEP
from homeassistant.components.climate.const import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.climate.const import HVACAction
from homeassistant.components.climate.const import HVACMode
from homeassistant.components.climate.const import PRESET_AWAY
from homeassistant.components.climate.const import PRESET_BOOST
from homeassistant.components.climate.const import PRESET_COMFORT
from homeassistant.components.climate.const import PRESET_NONE
from homeassistant.components.climate.const import PRESET_SLEEP
from homeassistant.components.climate.const import SERVICE_SET_HVAC_MODE
from homeassistant.components.climate.const import SERVICE_SET_PRESET_MODE
from homeassistant.components.climate.const import SERVICE_SET_TEMPERATURE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from keba_keenergy_api.constants import HeatCircuitOperatingMode
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import DEFAULT_POSITION_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_FIXED_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_RESPONSE
from tests.api_data import HEAT_CIRCUIT_OPERATION_MODE_3_DATA_RESPONSE
from tests.api_data import HEAT_CIRCUIT_OPERATION_MODE_4_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI

ENTITY_ID: str = "climate.keba_keenergy_12345678"
ENTITY_ID_1: str = "climate.keba_keenergy_12345678_1"
ENTITY_ID_2: str = "climate.keba_keenergy_12345678_2"


@pytest.mark.parametrize(
    ("response", "entities"),
    [
        (
            [
                DEFAULT_POSITION_RESPONSE,
                DEFAULT_POSITION_FIXED_DATA_RESPONSE,
                DEFAULT_POSITION_DATA_RESPONSE,
            ],
            [ENTITY_ID],
        ),
        (
            [
                MULTIPLE_POSITIONS_RESPONSE,
                get_multiple_position_fixed_data_response(),
                MULTIPLE_POSITIONS_DATA_RESPONSE,
            ],
            [ENTITY_ID_1, ENTITY_ID_2],
        ),
    ],
)
async def test_climate_entities(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    response: list[list[dict[str, Any]]],
    entities: list[str],
) -> None:
    """Test climate entities."""
    fake_api.responses = response
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    for entity in entities:
        assert isinstance(hass.states.get(entity), State)


async def test_climate(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test climate."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    state_1: State | None = hass.states.get(ENTITY_ID_1)
    assert isinstance(state_1, State)

    assert state_1.attributes[ATTR_CURRENT_TEMPERATURE] == 22.4
    assert state_1.attributes[ATTR_CURRENT_HUMIDITY] == 53.0

    state_2: State | None = hass.states.get(ENTITY_ID_2)
    assert isinstance(state_2, State)

    assert state_2.attributes[ATTR_HVAC_MODES] == [HVACMode.AUTO, HVACMode.HEAT, HVACMode.OFF]
    assert state_2.attributes[ATTR_MIN_TEMP] == 18.0
    assert state_2.attributes[ATTR_MAX_TEMP] == 23.0
    assert state_2.attributes[ATTR_TARGET_TEMP_STEP] == 0.5
    assert state_2.attributes[ATTR_PRESET_MODES] == ["none", "away", "comfort", "sleep", "boost"]
    assert state_2.attributes[ATTR_TEMPERATURE] == 20.5
    assert not state_2.attributes.get(ATTR_CURRENT_TEMPERATURE)
    assert not state_2.attributes.get(ATTR_CURRENT_HUMIDITY)
    assert state_2.attributes[ATTR_HVAC_ACTION] == HVACAction.OFF
    assert state_2.attributes[ATTR_PRESET_MODE] == "none"
    assert state_2.attributes[ATTR_FRIENDLY_NAME] == "Heating circuit 2"


async def test_climate_translations(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test climate."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    state_1: State | None = hass.states.get(ENTITY_ID_1)
    assert isinstance(state_1, State)
    assert state_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1"

    state_2: State | None = hass.states.get(ENTITY_ID_2)
    assert isinstance(state_2, State)
    assert state_2.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 2"


@pytest.mark.parametrize(
    ("responses", "expected_target_temperature"),
    [
        (HEAT_CIRCUIT_OPERATION_MODE_3_DATA_RESPONSE, 21.5),  # Night temperature 20.0 + Offset 1.5
        (HEAT_CIRCUIT_OPERATION_MODE_4_DATA_RESPONSE, 19.5),  # Holiday temperature 18.0 + Offset 1.5
    ],
)
async def test_target_temperature(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    responses: list[dict[str, Any]],
    expected_target_temperature: float,
) -> None:
    """Test target temperature."""
    fake_api.responses = [
        DEFAULT_POSITION_RESPONSE,
        DEFAULT_POSITION_FIXED_DATA_RESPONSE,
        responses,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    state: State | None = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)

    assert state.attributes[ATTR_TEMPERATURE] == expected_target_temperature


async def test_turn_off(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test turn on climate."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_TURN_OFF,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        f'[{{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode", '
        f'"value": "{HeatCircuitOperatingMode.OFF.value}"}}]',
    )


async def test_turn_on(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test turn on climate."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_TURN_ON,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        f'[{{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode", '
        f'"value": "{HeatCircuitOperatingMode.AUTO.value}"}}]',
    )


@pytest.mark.parametrize(
    ("hvac_mode", "expected_hvac_mode"),
    [
        (HVACMode.AUTO, 1),
        (HVACMode.HEAT, 2),
        (HVACMode.OFF, 0),
    ],
)
async def test_set_hvac_mode(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hvac_mode: str,
    expected_hvac_mode: str,
) -> None:
    """Test set preset mode."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_HVAC_MODE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
            ATTR_HVAC_MODE: hvac_mode,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        f'[{{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode", "value": "{expected_hvac_mode}"}}]',
    )


@pytest.mark.parametrize(
    ("preset_mode", "expected_preset_mode"),
    [
        (PRESET_NONE, HeatCircuitOperatingMode.AUTO.value),
        (PRESET_AWAY, HeatCircuitOperatingMode.HOLIDAY.value),
        (PRESET_COMFORT, HeatCircuitOperatingMode.DAY.value),
        (PRESET_SLEEP, HeatCircuitOperatingMode.NIGHT.value),
        (PRESET_BOOST, HeatCircuitOperatingMode.PARTY.value),
    ],
)
async def test_set_preset_mode(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    preset_mode: str,
    expected_preset_mode: str,
) -> None:
    """Test set preset mode."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
            ATTR_PRESET_MODE: preset_mode,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        f'[{{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode", "value": "{expected_preset_mode}"}}]',
    )


async def test_set_temperature(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test setting temperature."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
            ATTR_TEMPERATURE: 19.5,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp", "value": "-1.0"}]',
    )
