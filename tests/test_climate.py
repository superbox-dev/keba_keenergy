# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the climate entities."""

from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.components.climate.const import ATTR_HVAC_MODE
from homeassistant.components.climate.const import ATTR_PRESET_MODE
from homeassistant.components.climate.const import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.climate.const import PRESET_AWAY
from homeassistant.components.climate.const import PRESET_BOOST
from homeassistant.components.climate.const import PRESET_COMFORT
from homeassistant.components.climate.const import PRESET_HOME
from homeassistant.components.climate.const import PRESET_SLEEP
from homeassistant.components.climate.const import SERVICE_SET_HVAC_MODE
from homeassistant.components.climate.const import SERVICE_SET_PRESET_MODE
from homeassistant.components.climate.const import SERVICE_SET_TEMPERATURE
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.util import dt as dt_util
from keba_keenergy_api.constants import HeatCircuitOperatingMode
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.keba_keenergy.const import FLASH_WRITE_DELAY
from tests import get_platform_states
from tests.api_data import DEFAULT_POSITION_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_FIXED_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_2
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response
from tests.api_data import get_single_position_data_response
from tests.api_data import update_response

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion

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
                MULTIPLE_POSITION_DATA_RESPONSE_1,
            ],
            [ENTITY_ID_1, ENTITY_ID_2],
        ),
    ],
)
async def test_climate_entities(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    response: list[list[dict[str, Any]]],
    entities: list[str],
) -> None:
    """Test that the climate entities are created for the heating circuits."""
    fake_api.responses = [*response]
    await fake_api.setup_integration()

    for entity in entities:
        assert isinstance(hass.states.get(entity), State)


@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_climate(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all climate entities."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.CLIMATE):
        assert state == snapshot(name=state.entity_id)


@pytest.mark.parametrize(
    ("responses", "expected_target_temperature"),
    [
        (
            get_single_position_data_response(heat_circuit_target_temperature_offset="1.5"),
            21.5,
        ),  # Selected target temperature 20.0 + Offset 1.5
    ],
)
async def test_target_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    responses: list[dict[str, Any]],
    expected_target_temperature: float,
) -> None:
    """Test the target temperature of the climate entity."""
    fake_api.responses = [
        DEFAULT_POSITION_RESPONSE,
        DEFAULT_POSITION_FIXED_DATA_RESPONSE,
        responses,
    ]
    await fake_api.setup_integration()

    state: State | None = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)

    assert state.attributes[ATTR_TEMPERATURE] == expected_target_temperature


async def test_set_temperature_debounced(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that quick target temperature changes are shown at once and written once, with the last value."""
    fake_api.responses = [
        DEFAULT_POSITION_RESPONSE,
        DEFAULT_POSITION_FIXED_DATA_RESPONSE,
        get_single_position_data_response(heat_circuit_target_temperature_offset="1.5"),
        # Read API after updating the entity
        get_single_position_data_response(heat_circuit_target_temperature_offset="1.5"),
    ]
    await fake_api.setup_integration()

    temperatures: tuple[float, ...] = (21.0, 20.5)

    for temperature in temperatures:
        await hass.services.async_call(
            domain=CLIMATE_DOMAIN,
            service=SERVICE_SET_TEMPERATURE,
            service_data={
                ATTR_ENTITY_ID: ENTITY_ID,
                ATTR_TEMPERATURE: temperature,
            },
            blocking=True,
        )

    await async_update_entity(hass, ENTITY_ID)

    state: State | None = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)
    assert state.attributes[ATTR_TEMPERATURE] == temperatures[-1]
    assert fake_api.write_requests() == []

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=FLASH_WRITE_DELAY))
    await hass.async_block_till_done()

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp", "value": "0.5"}]',
    ]


async def test_set_temperature_without_selected_target_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that no offset is written if the Web HMI does not provide the selected target temperature."""
    fake_api.unsupported_variables = {"APPL.CtrlAppl.sParam.heatCircuit[0].values.selectedSetTemp"}
    fake_api.responses = [
        DEFAULT_POSITION_RESPONSE,
        DEFAULT_POSITION_FIXED_DATA_RESPONSE,
        get_single_position_data_response(),
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID,
            ATTR_TEMPERATURE: 21.0,
        },
        blocking=True,
    )

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=FLASH_WRITE_DELAY))
    await hass.async_block_till_done()

    state: State | None = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)
    assert state.attributes[ATTR_TEMPERATURE] is None
    assert fake_api.write_requests() == []


async def test_turn_off(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test turning off a heating circuit."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

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
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test turning on a heating circuit."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

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
    fake_api: FakeKebaKeEnergyAPI,
    hvac_mode: str,
    expected_hvac_mode: str,
) -> None:
    """Test setting the HVAC mode of a heating circuit in holiday mode."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_2,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_2,
    ]
    await fake_api.setup_integration()

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


async def test_set_unchanged_hvac_mode(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the HVAC mode is not written if the heating circuit already has it."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_HVAC_MODE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
            ATTR_HVAC_MODE: HVACMode.HEAT,
        },
        blocking=True,
    )

    assert fake_api.write_requests() == []


@pytest.mark.parametrize(
    ("preset_mode", "response", "expected_preset_mode"),
    [
        (PRESET_HOME, MULTIPLE_POSITION_DATA_RESPONSE_1, HeatCircuitOperatingMode.AUTO.value),
        (PRESET_COMFORT, MULTIPLE_POSITION_DATA_RESPONSE_2, HeatCircuitOperatingMode.DAY.value),
        (PRESET_SLEEP, MULTIPLE_POSITION_DATA_RESPONSE_1, HeatCircuitOperatingMode.NIGHT.value),
        (PRESET_BOOST, MULTIPLE_POSITION_DATA_RESPONSE_1, HeatCircuitOperatingMode.PARTY.value),
    ],
)
async def test_set_preset_mode(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    preset_mode: str,
    response: list[dict[str, Any]],
    expected_preset_mode: str,
) -> None:
    """Test setting the preset mode of a heating circuit."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        response,
        # Read API after services call
        response,
    ]
    await fake_api.setup_integration()

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


async def test_set_preset_mode_away(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the preset mode away sets the away date range."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    with patch.object(dt_util, "now", return_value=datetime(2026, 1, 24, 12, 0, tzinfo=UTC)):
        await hass.services.async_call(
            domain=CLIMATE_DOMAIN,
            service=SERVICE_SET_PRESET_MODE,
            service_data={
                ATTR_ENTITY_ID: ENTITY_ID_1,
                ATTR_PRESET_MODE: PRESET_AWAY,
            },
            blocking=True,
        )

    fake_api.assert_called_write_with(
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.start", "value": "1769209200"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.start", "value": "1769209200"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.stop", "value": "1800831599"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.stop", "value": "1800831599"}]',
    )


async def test_unset_preset_mode_away(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that leaving the preset mode away resets the away date range."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_2,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    with patch.object(dt_util, "now", return_value=datetime(2026, 1, 24, 12, 0, tzinfo=UTC)):
        await hass.services.async_call(
            domain=CLIMATE_DOMAIN,
            service=SERVICE_SET_PRESET_MODE,
            service_data={
                ATTR_ENTITY_ID: ENTITY_ID_1,
                ATTR_PRESET_MODE: PRESET_COMFORT,
            },
            blocking=True,
        )

    fake_api.assert_called_write_with(
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode", "value": "2"}]',
    )

    fake_api.assert_called_write_with(
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.start", "value": "1769122800"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.start", "value": "1769122800"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.stop", "value": "1769209199"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.stop", "value": "1769209199"}]',
    )


async def test_set_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test setting the target temperature of a heating circuit."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
            ATTR_TEMPERATURE: 19.5,
        },
        blocking=True,
    )

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
    await hass.async_block_till_done()

    fake_api.assert_called_write_with(
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp", "value": "-0.5"}]',
    )


@pytest.mark.parametrize(
    "operating_mode",
    [HeatCircuitOperatingMode.EXTERNAL, HeatCircuitOperatingMode.ROOM_CONTROL],
)
async def test_operating_mode_without_preset(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    operating_mode: HeatCircuitOperatingMode,
) -> None:
    """Test that a heating circuit in an operating mode without a preset has the home preset."""
    fake_api.responses = [
        DEFAULT_POSITION_RESPONSE,
        DEFAULT_POSITION_FIXED_DATA_RESPONSE,
        update_response(
            get_single_position_data_response(),
            "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode",
            value=str(operating_mode.value),
        ),
    ]
    await fake_api.setup_integration()

    state: State | None = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)
    assert state.state == HVACMode.OFF
    assert state.attributes[ATTR_PRESET_MODE] == PRESET_HOME


async def test_set_preset_mode_without_time_zone_request(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a preset mode change outside of away does not request the time zone."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
            ATTR_PRESET_MODE: PRESET_BOOST,
        },
        blocking=True,
    )

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode", "value": "5"}]',
    ]
    assert not [url for _, url, *_ in fake_api.aioclient_mock.mock_calls if url.path == "/dateTime"]
