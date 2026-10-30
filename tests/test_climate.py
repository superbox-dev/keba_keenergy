# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the climate entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
from homeassistant.components.climate.const import DEFAULT_MAX_TEMP
from homeassistant.components.climate.const import DEFAULT_MIN_TEMP
from homeassistant.components.climate.const import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.climate.const import PRESET_AWAY
from homeassistant.components.climate.const import PRESET_BOOST
from homeassistant.components.climate.const import PRESET_COMFORT
from homeassistant.components.climate.const import PRESET_HOME
from homeassistant.components.climate.const import PRESET_SLEEP
from homeassistant.components.climate.const import SERVICE_SET_HVAC_MODE
from homeassistant.components.climate.const import SERVICE_SET_PRESET_MODE
from homeassistant.components.climate.const import HVACAction
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import Platform
from homeassistant.exceptions import HomeAssistantError
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_component import async_update_entity
from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import HeatingCircuitRequest
from keba_keenergy_api.enums import HeatingCircuitType
from keba_keenergy_api.enums import HeatPumpState

from tests import fire_debounced_writes
from tests import get_platform_states
from tests import get_state
from tests import set_target_temperature
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE
from tests.api_data import Response
from tests.api_data import get_multiple_devices_responses
from tests.api_data import get_single_device_data_response
from tests.api_data import get_single_device_responses
from tests.api_data import update_response
from tests.test_climate_data import AWAY_DATE_RANGE_RESET_WRITE
from tests.test_climate_data import AWAY_PRESET_WRITE
from tests.test_climate_data import HEAT_CIRCUIT_1_ENTITY_ID
from tests.test_climate_data import HEAT_CIRCUIT_ENTITY_ID
from tests.test_climate_data import NOW
from tests.test_climate_data import PARTY_DATA_RESPONSE
from tests.test_climate_data import REDUCED_DATA_RESPONSE
from tests.test_climate_data import TARGET_TEMPERATURE_WITH_OFFSET
from tests.test_climate_data import get_circuit_type_responses
from tests.test_climate_data import get_hvac_action_data_response
from tests.test_climate_data import get_operating_mode_write

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
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


@pytest.mark.parametrize(
    ("circuit_type", "expected_modes"),
    [
        (
            HeatingCircuitType.HEATING,
            (
                [HVACMode.AUTO, HVACMode.HEAT, HVACMode.OFF],
                [PRESET_HOME, PRESET_AWAY, PRESET_COMFORT, PRESET_SLEEP, PRESET_BOOST],
            ),
        ),
        (
            HeatingCircuitType.COOLING,
            (
                [HVACMode.AUTO, HVACMode.COOL, HVACMode.OFF],
                [PRESET_HOME, PRESET_COMFORT, PRESET_SLEEP, PRESET_BOOST],
            ),
        ),
        (
            HeatingCircuitType.HEATING_AND_COOLING,
            (
                [HVACMode.AUTO, HVACMode.HEAT_COOL, HVACMode.OFF],
                [PRESET_HOME, PRESET_AWAY, PRESET_COMFORT, PRESET_SLEEP, PRESET_BOOST],
            ),
        ),
    ],
    ids=["heating", "cooling", "heating_and_cooling"],
)
async def test_hvac_and_preset_modes(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    circuit_type: HeatingCircuitType,
    expected_modes: tuple[list[HVACMode], list[str]],
) -> None:
    """Test that the HVAC modes and presets depend on the type of the heating circuit, only cooling has no away."""
    fake_api.responses = get_circuit_type_responses(circuit_type)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)

    assert (state.attributes[ATTR_HVAC_MODES], state.attributes[ATTR_PRESET_MODES]) == expected_modes


async def test_set_hvac_mode_cool(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the HVAC mode cool of a heating circuit that only cools writes the operating mode normal."""
    fake_api.responses = get_circuit_type_responses(HeatingCircuitType.COOLING, operating_mode="0")
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_HVAC_MODE,
        service_data={
            ATTR_ENTITY_ID: HEAT_CIRCUIT_ENTITY_ID,
            ATTR_HVAC_MODE: HVACMode.COOL,
        },
        blocking=True,
    )

    assert fake_api.write_requests() == [get_operating_mode_write(HeatingCircuitOperatingMode.NORMAL)]


async def test_set_preset_mode_away_of_cooling_circuit(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a heating circuit that only cools rejects the away preset."""
    fake_api.responses = get_circuit_type_responses(HeatingCircuitType.COOLING)
    await fake_api.setup_integration()

    with pytest.raises(ServiceValidationError) as error:
        await hass.services.async_call(
            domain=CLIMATE_DOMAIN,
            service=SERVICE_SET_PRESET_MODE,
            service_data={
                ATTR_ENTITY_ID: HEAT_CIRCUIT_ENTITY_ID,
                ATTR_PRESET_MODE: PRESET_AWAY,
            },
            blocking=True,
        )

    assert error.value.translation_key == "not_valid_preset_mode"
    assert fake_api.write_requests() == []


@pytest.mark.parametrize(
    ("response", "expected_limits"),
    [
        # The selected target temperature 20.0 plus the limits of the offset (-2.5 and 2.5).
        (get_single_device_data_response(), (17.5, 22.5)),
        (
            update_response(
                get_single_device_data_response(),
                "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp",
                attributes={},
            ),
            (DEFAULT_MIN_TEMP, DEFAULT_MAX_TEMP),
        ),
    ],
    ids=["offset_limits", "without_limits"],
)
async def test_temperature_limits(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    response: Response,
    expected_limits: tuple[float, float],
) -> None:
    """Test the limits of the target temperature, the defaults of Home Assistant without the limits of the offset."""
    fake_api.responses = get_single_device_responses(response)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)

    assert (state.attributes[ATTR_MIN_TEMP], state.attributes[ATTR_MAX_TEMP]) == expected_limits


async def test_set_temperature_out_of_range(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a target temperature outside of the limits is rejected and not written."""
    fake_api.responses = get_single_device_responses(get_single_device_data_response())
    await fake_api.setup_integration()

    with pytest.raises(ServiceValidationError) as error:
        await set_target_temperature(hass, HEAT_CIRCUIT_ENTITY_ID, 23.0)

    await fire_debounced_writes(hass)

    assert error.value.translation_key == "temp_out_of_range"
    assert fake_api.write_requests() == []


async def test_target_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the target temperature is the selected target temperature 20.0 plus the offset 1.5."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
    )
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
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
        await set_target_temperature(hass, HEAT_CIRCUIT_ENTITY_ID, temperature)

    await async_update_entity(hass, HEAT_CIRCUIT_ENTITY_ID)

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == temperatures[-1]
    assert fake_api.write_requests() == []

    await fire_debounced_writes(hass)

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

    await set_target_temperature(hass, HEAT_CIRCUIT_ENTITY_ID, 21.0)

    await fire_debounced_writes(hass)

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] is None
    assert fake_api.write_requests() == []


@pytest.mark.parametrize(
    ("service_call", "response", "expected_writes"),
    [
        (
            (SERVICE_TURN_OFF, {}),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [get_operating_mode_write(HeatingCircuitOperatingMode.OFF)],
        ),
        (
            (SERVICE_TURN_ON, {}),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [get_operating_mode_write(HeatingCircuitOperatingMode.AUTO)],
        ),
        ((SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}), MULTIPLE_DEVICES_DATA_RESPONSE, []),
        ((SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}), REDUCED_DATA_RESPONSE, []),
        ((SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}), PARTY_DATA_RESPONSE, []),
        (
            (SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.AUTO}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.AUTO)],
        ),
        (
            (SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.NORMAL)],
        ),
        (
            (SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.OFF}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.OFF)],
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
        service_data={ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID, **service_data},
        blocking=True,
    )

    assert fake_api.write_requests() == expected_writes


@pytest.mark.parametrize(
    ("preset_mode", "response", "expected"),
    [
        (
            PRESET_HOME,
            MULTIPLE_DEVICES_DATA_RESPONSE,
            ([get_operating_mode_write(HeatingCircuitOperatingMode.AUTO)], 0),
        ),
        (PRESET_COMFORT, MULTIPLE_DEVICES_DATA_RESPONSE, ([], 0)),
        (
            PRESET_SLEEP,
            MULTIPLE_DEVICES_DATA_RESPONSE,
            ([get_operating_mode_write(HeatingCircuitOperatingMode.REDUCED)], 0),
        ),
        (
            PRESET_BOOST,
            MULTIPLE_DEVICES_DATA_RESPONSE,
            ([get_operating_mode_write(HeatingCircuitOperatingMode.PARTY)], 0),
        ),
        (PRESET_AWAY, MULTIPLE_DEVICES_DATA_RESPONSE, ([AWAY_PRESET_WRITE], 1)),
        (
            PRESET_HOME,
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            ([AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.AUTO)], 1),
        ),
        (
            PRESET_COMFORT,
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            ([AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.NORMAL)], 1),
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
    expected: tuple[list[str], int],
) -> None:
    """Test setting the preset mode of a heating circuit.

    The away preset sets an away date range of one year, leaving it resets the date range to yesterday. Only a
    change of the away date range requests the time zone of the Web HMI (the second expected value).
    """
    fake_api.responses = get_multiple_devices_responses(response)
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={
            ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID,
            ATTR_PRESET_MODE: preset_mode,
        },
        blocking=True,
    )

    assert (fake_api.write_requests(), fake_api.time_zone_request_count()) == expected


@pytest.mark.parametrize(
    ("preset_mode", "responses", "expected_preset_mode"),
    [
        (PRESET_AWAY, (MULTIPLE_DEVICES_DATA_RESPONSE, MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE), PRESET_AWAY),
        (PRESET_HOME, (MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE, MULTIPLE_DEVICES_DATA_RESPONSE), PRESET_COMFORT),
    ],
    ids=["away", "home_while_away"],
)
@pytest.mark.freeze_time(NOW)
async def test_set_preset_mode_refreshes_target_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    preset_mode: str,
    responses: tuple[Response, Response],
    expected_preset_mode: str,
) -> None:
    """Test that a preset change reads the values again, the control unit knows the target temperature of the mode."""
    fake_api.responses = get_multiple_devices_responses(*responses)
    await fake_api.setup_integration()
    read_count: int = len(fake_api.read_requests())

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={
            ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID,
            ATTR_PRESET_MODE: preset_mode,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    assert len(fake_api.read_requests()) == read_count + 1
    assert get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID).attributes[ATTR_PRESET_MODE] == expected_preset_mode


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
                ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID,
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

    await set_target_temperature(hass, HEAT_CIRCUIT_1_ENTITY_ID, 19.5)

    await fire_debounced_writes(hass)

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

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
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

    state: State = get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID)
    assert (state.state, state.attributes[ATTR_CURRENT_TEMPERATURE], state.attributes[ATTR_CURRENT_HUMIDITY]) == (
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
        "pre_run",
        "automatic",
        "defrost",
        "cooling",
        "post_run",
        "pump_down",
        "shutdown",
        "error",
        "source_flush",
        "automatic_hot_water_priority",
        "standby_cool_request",
        "standby_cool_request_outdoor_off",
        "automatic_hvac_mode_off",
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

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
    assert state.attributes[ATTR_HVAC_ACTION] == expected_hvac_action
