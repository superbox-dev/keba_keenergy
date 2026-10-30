# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the climate entities."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import pytest
from homeassistant.components.climate.const import ATTR_HVAC_ACTION
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
from homeassistant.components.climate.const import HVACAction
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.util import dt as dt_util
from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import HeatingCircuitOperatingMode as Mode
from keba_keenergy_api.enums import HeatingCircuitRequest
from keba_keenergy_api.enums import HeatPumpState
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.keba_keenergy.const import FLASH_WRITE_DELAY
from tests import get_platform_states
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE
from tests.api_data import Response
from tests.api_data import get_multiple_devices_responses
from tests.api_data import get_single_device_data_response
from tests.api_data import get_single_device_responses
from tests.api_data import update_response
from tests.test_climate_data import AWAY_DATE_RANGE_RESET_WRITE
from tests.test_climate_data import AWAY_DATE_RANGE_WRITE
from tests.test_climate_data import ENTITY_ID
from tests.test_climate_data import ENTITY_ID_1
from tests.test_climate_data import NOW
from tests.test_climate_data import PARTY_DATA_RESPONSE
from tests.test_climate_data import REDUCED_DATA_RESPONSE
from tests.test_climate_data import TARGET_TEMPERATURE_WITH_OFFSET
from tests.test_climate_data import get_hvac_action_data_response
from tests.test_climate_data import get_operating_mode_write

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_climate(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all climate entities."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.CLIMATE):
        assert state == snapshot(name=state.entity_id)


async def test_target_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the target temperature is the selected target temperature 20.0 plus the offset 1.5."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
    )
    await fake_api.setup_integration()

    state: State | None = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)
    assert state.attributes[ATTR_TEMPERATURE] == TARGET_TEMPERATURE_WITH_OFFSET


async def test_set_temperature_debounced(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that quick target temperature changes are shown at once and written once, with the last value."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
        # Read the API after the update of the entity.
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
    )
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
    fake_api.responses = get_single_device_responses(get_single_device_data_response())
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


@pytest.mark.parametrize(
    ("service_call", "response", "expected_writes"),
    [
        ((SERVICE_TURN_OFF, {}), MULTIPLE_DEVICES_DATA_RESPONSE, [get_operating_mode_write(Mode.OFF)]),
        ((SERVICE_TURN_ON, {}), MULTIPLE_DEVICES_DATA_RESPONSE, [get_operating_mode_write(Mode.AUTO)]),
        ((SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}), MULTIPLE_DEVICES_DATA_RESPONSE, []),
        ((SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}), REDUCED_DATA_RESPONSE, []),
        ((SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}), PARTY_DATA_RESPONSE, []),
        (
            (SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.AUTO}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(Mode.AUTO)],
        ),
        (
            (SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(Mode.NORMAL)],
        ),
        (
            (SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.OFF}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(Mode.OFF)],
        ),
    ],
    ids=[
        "turn_off",
        "turn_on",
        "unchanged",
        "heat_while_reduced",
        "heat_while_party",
        "auto_while_away",
        "heat_while_away",
        "off_while_away",
    ],
)
@pytest.mark.freeze_time(NOW)
async def test_set_hvac_mode(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    service_call: tuple[str, dict[str, HVACMode]],
    response: Response,
    expected_writes: list[str],
) -> None:
    """Test setting the HVAC mode of a heating circuit, only a change is written.

    An HVAC mode that is already active keeps the preset, every HVAC mode ends the away date range.
    """
    fake_api.responses = get_multiple_devices_responses(response)
    await fake_api.setup_integration()

    service, service_data = service_call
    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=service,
        service_data={ATTR_ENTITY_ID: ENTITY_ID_1, **service_data},
        blocking=True,
    )

    assert fake_api.write_requests() == expected_writes


@pytest.mark.parametrize(
    ("preset_mode", "response", "expected_writes"),
    [
        (PRESET_HOME, MULTIPLE_DEVICES_DATA_RESPONSE, [get_operating_mode_write(Mode.AUTO)]),
        (PRESET_COMFORT, MULTIPLE_DEVICES_DATA_RESPONSE, []),
        (PRESET_SLEEP, MULTIPLE_DEVICES_DATA_RESPONSE, [get_operating_mode_write(Mode.REDUCED)]),
        (PRESET_BOOST, MULTIPLE_DEVICES_DATA_RESPONSE, [get_operating_mode_write(Mode.PARTY)]),
        (PRESET_AWAY, MULTIPLE_DEVICES_DATA_RESPONSE, [AWAY_DATE_RANGE_WRITE]),
        (
            PRESET_HOME,
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(Mode.AUTO)],
        ),
        (
            PRESET_COMFORT,
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(Mode.NORMAL)],
        ),
    ],
    ids=["home", "comfort_unchanged", "sleep", "boost", "away", "home_while_away", "comfort_while_away"],
)
@pytest.mark.freeze_time(NOW)
async def test_set_preset_mode(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    preset_mode: str,
    response: Response,
    expected_writes: list[str],
) -> None:
    """Test setting the preset mode of a heating circuit.

    The away preset sets an away date range of one year, leaving it resets the date range to yesterday. Only a
    change of the away date range requests the time zone of the Web HMI.
    """
    fake_api.responses = get_multiple_devices_responses(response)
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

    assert fake_api.write_requests() == expected_writes
    assert len([url for _, url, *_ in fake_api.aioclient_mock.mock_calls if url.path == "/dateTime"]) == len(
        [write for write in expected_writes if "holiday" in write],
    )


async def test_set_preset_mode_away_with_invalid_time_zone(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that an invalid time zone of the Web HMI raises a translated error and writes nothing."""
    fake_api.timezone = "Invalid/Zone"
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    with pytest.raises(HomeAssistantError) as error:
        await hass.services.async_call(
            domain=CLIMATE_DOMAIN,
            service=SERVICE_SET_PRESET_MODE,
            service_data={
                ATTR_ENTITY_ID: ENTITY_ID_1,
                ATTR_PRESET_MODE: PRESET_AWAY,
            },
            blocking=True,
        )

    assert error.value.translation_key == "invalid_time_zone"
    assert error.value.translation_placeholders == {"time_zone": "Invalid/Zone"}
    assert fake_api.write_requests() == []


async def test_set_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test setting the target temperature of a heating circuit."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
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

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=FLASH_WRITE_DELAY))
    await hass.async_block_till_done()

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp", "value": "-0.5"}]'
    ]


@pytest.mark.parametrize(
    "operating_mode",
    [HeatingCircuitOperatingMode.EXTERNAL, HeatingCircuitOperatingMode.ROOM_CONTROL],
    ids=["external", "room_control"],
)
async def test_operating_mode_without_preset(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    operating_mode: HeatingCircuitOperatingMode,
) -> None:
    """Test that a heating circuit in an operating mode without a preset has the home preset."""
    fake_api.responses = get_single_device_responses(
        update_response(
            get_single_device_data_response(),
            "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode",
            value=str(operating_mode.value),
        ),
    )
    await fake_api.setup_integration()

    state: State | None = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)
    assert state.state == HVACMode.OFF
    assert state.attributes[ATTR_PRESET_MODE] == PRESET_HOME


async def test_room_sensor_not_in_use(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the climate entity has no current temperature if the room sensor is not in use (message id not 0).

    The climate entity stays available, the room humidity sensor is still in use.
    """
    fake_api.message_ids = {"APPL.CtrlAppl.sParam.heatCircuit[0].tempRoom.state.msgId": 10}
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    state: State | None = hass.states.get(ENTITY_ID_1)
    assert isinstance(state, State)
    assert (state.state, state.attributes["current_temperature"], state.attributes["current_humidity"]) == (
        HVACMode.HEAT,
        None,
        53.0,
    )


@pytest.mark.parametrize(
    ("response", "expected_hvac_action"),
    [
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.STANDBY), HVACAction.IDLE),
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.PRE_RUN), HVACAction.PREHEATING),
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.AUTOMATIC), HVACAction.HEATING),
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.DEFROST), HVACAction.DEFROSTING),
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.COOLING), HVACAction.IDLE),
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.POST_RUN), HVACAction.HEATING),
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.PUMP_DOWN), HVACAction.IDLE),
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.SHUTDOWN), HVACAction.IDLE),
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.ERROR), HVACAction.IDLE),
        (get_hvac_action_data_response(heat_pump_state=HeatPumpState.SOURCE_FLUSH), HVACAction.IDLE),
        # The heat request of the heating circuit is temporarily off while the heat pump heats the hot water.
        (
            get_hvac_action_data_response(
                heat_pump_state=HeatPumpState.AUTOMATIC,
                heat_request=HeatingCircuitRequest.TEMPERATURE_PRIORITY_OFF,
            ),
            HVACAction.IDLE,
        ),
        # The heat pump stays in standby with passive cooling.
        (
            get_hvac_action_data_response(
                heat_pump_state=HeatPumpState.STANDBY,
                heat_request=HeatingCircuitRequest.OFF,
                cool_request=HeatingCircuitRequest.ACTIVE,
            ),
            HVACAction.COOLING,
        ),
        (
            get_hvac_action_data_response(
                heat_pump_state=HeatPumpState.STANDBY,
                heat_request=HeatingCircuitRequest.OFF,
                cool_request=HeatingCircuitRequest.OUTDOOR_OFF,
            ),
            HVACAction.IDLE,
        ),
        (
            get_hvac_action_data_response(
                heat_pump_state=HeatPumpState.AUTOMATIC,
                operating_mode=HeatingCircuitOperatingMode.OFF,
            ),
            HVACAction.OFF,
        ),
    ],
    ids=[
        "standby",
        "flow",
        "auto_heat",
        "defrost",
        "auto_cool",
        "inflow",
        "pump_down",
        "shutdown",
        "error",
        "source_flush",
        "hot_water",
        "cool_request",
        "no_request",
        "hvac_mode_off",
    ],
)
async def test_hvac_action(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    response: Response,
    expected_hvac_action: HVACAction,
) -> None:
    """Test the action of a heating circuit with the requests of the heating circuit and the heat pump state."""
    fake_api.responses = get_single_device_responses(response)
    await fake_api.setup_integration()

    state: State | None = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)
    assert state.attributes[ATTR_HVAC_ACTION] == expected_hvac_action
