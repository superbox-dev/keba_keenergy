# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the water heater entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.water_heater import ATTR_CURRENT_TEMPERATURE
from homeassistant.components.water_heater import ATTR_MAX_TEMP
from homeassistant.components.water_heater import ATTR_MIN_TEMP
from homeassistant.components.water_heater import ATTR_OPERATION_MODE
from homeassistant.components.water_heater import SERVICE_SET_OPERATION_MODE
from homeassistant.components.water_heater.const import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.components.water_heater.const import STATE_ECO
from homeassistant.components.water_heater.const import STATE_HEAT_PUMP
from homeassistant.components.water_heater.const import STATE_PERFORMANCE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import STATE_OFF
from homeassistant.const import Platform
from homeassistant.helpers.entity_component import async_update_entity

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
from tests.test_water_heater_data import BUFFER_TANK
from tests.test_water_heater_data import BUFFER_TANK_1_ENTITY_ID
from tests.test_water_heater_data import DEFAULT_LIMITS
from tests.test_water_heater_data import HOT_WATER_TANK
from tests.test_water_heater_data import HOT_WATER_TANK_1_ENTITY_ID
from tests.test_water_heater_data import HOT_WATER_TANK_2_ENTITY_ID
from tests.test_water_heater_data import HOT_WATER_TANK_ENTITY_ID
from tests.test_water_heater_data import get_operating_mode_write

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_water_heater(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all water heater entities."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.WATER_HEATER):
        assert state == snapshot(name=state.entity_id)


@pytest.mark.parametrize(
    ("service_call", "response", "expected_writes"),
    [
        (
            (SERVICE_TURN_OFF, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [get_operating_mode_write(HOT_WATER_TANK, 0)],
        ),
        ((SERVICE_TURN_OFF, {ATTR_ENTITY_ID: HOT_WATER_TANK_2_ENTITY_ID}), MULTIPLE_DEVICES_DATA_RESPONSE, []),
        (
            (SERVICE_TURN_OFF, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [get_operating_mode_write(BUFFER_TANK, 0)],
        ),
        ((SERVICE_TURN_OFF, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID}), MULTIPLE_DEVICES_DATA_RESPONSE, []),
        (
            (SERVICE_TURN_ON, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID}),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [get_operating_mode_write(HOT_WATER_TANK, 2)],
        ),
        (
            (SERVICE_TURN_ON, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [],
        ),
        (
            (SERVICE_TURN_ON, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID}),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [get_operating_mode_write(BUFFER_TANK, 1)],
        ),
        ((SERVICE_TURN_ON, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID}), MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE, []),
        (
            (SERVICE_SET_OPERATION_MODE, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_ECO}),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [get_operating_mode_write(HOT_WATER_TANK, 1)],
        ),
        (
            (
                SERVICE_SET_OPERATION_MODE,
                {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_PERFORMANCE},
            ),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [get_operating_mode_write(HOT_WATER_TANK, 3)],
        ),
        (
            (SERVICE_SET_OPERATION_MODE, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_OFF}),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [get_operating_mode_write(HOT_WATER_TANK, 0)],
        ),
        (
            (
                SERVICE_SET_OPERATION_MODE,
                {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_HEAT_PUMP},
            ),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [get_operating_mode_write(HOT_WATER_TANK, 2)],
        ),
        (
            (
                SERVICE_SET_OPERATION_MODE,
                {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_PERFORMANCE},
            ),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [get_operating_mode_write(BUFFER_TANK, 2)],
        ),
        (
            (SERVICE_SET_OPERATION_MODE, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_OFF}),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [get_operating_mode_write(BUFFER_TANK, 0)],
        ),
        (
            (
                SERVICE_SET_OPERATION_MODE,
                {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_HEAT_PUMP},
            ),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [get_operating_mode_write(BUFFER_TANK, 1)],
        ),
    ],
    ids=[
        "hot_water_tank_turn_off",
        "hot_water_tank_turn_off_unchanged",
        "buffer_tank_turn_off",
        "buffer_tank_turn_off_unchanged",
        "hot_water_tank_turn_on",
        "hot_water_tank_turn_on_unchanged",
        "buffer_tank_turn_on",
        "buffer_tank_turn_on_unchanged",
        "hot_water_tank_eco",
        "hot_water_tank_performance",
        "hot_water_tank_off",
        "hot_water_tank_heat_pump",
        "buffer_tank_performance",
        "buffer_tank_off",
        "buffer_tank_heat_pump",
    ],
)
async def test_set_operation_mode(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    service_call: tuple[str, dict[str, str]],
    response: Response,
    expected_writes: list[str],
) -> None:
    """Test turning on and off and setting the operation mode of a tank, the current mode is not written again."""
    fake_api.responses = get_multiple_devices_responses(response)
    await fake_api.setup_integration()

    service, service_data = service_call
    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=service,
        service_data=service_data,
        blocking=True,
    )

    assert fake_api.write_requests() == expected_writes


async def test_set_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test setting the target temperature of a hot water tank."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    await set_target_temperature(hass, HOT_WATER_TANK_1_ENTITY_ID, 45)

    await fire_debounced_writes(hass)

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", "value": "45.0"}]',
    ]


async def test_set_temperature_debounced(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that quick target temperature changes are shown at once and written once, with the last value."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(hot_water_tank_target_temperature="51"),
        # Read the API after the update of the entity.
        get_single_device_data_response(hot_water_tank_target_temperature="51"),
    )
    await fake_api.setup_integration()

    temperatures: tuple[float, ...] = (45.0, 44.0)

    for temperature in temperatures:
        await set_target_temperature(hass, HOT_WATER_TANK_ENTITY_ID, temperature)

    await async_update_entity(hass, HOT_WATER_TANK_ENTITY_ID)

    state: State = get_state(hass, HOT_WATER_TANK_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == temperatures[-1]
    assert fake_api.write_requests() == []

    await fire_debounced_writes(hass)

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", "value": "44.0"}]',
    ]


async def test_set_unchanged_target_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the current target temperature of a hot water tank is not written again."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(hot_water_tank_target_temperature="51"),
    )
    await fake_api.setup_integration()

    await set_target_temperature(hass, HOT_WATER_TANK_ENTITY_ID, 51)

    await fire_debounced_writes(hass)

    assert fake_api.write_requests() == []


async def test_limits_after_update(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a hot water tank uses the limits from the API once an update provides them."""
    fake_api.responses = get_single_device_responses(
        update_response(
            get_single_device_data_response(),
            "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value",
            attributes={},
        ),
        get_single_device_data_response(),
    )
    await fake_api.setup_integration()

    state: State = get_state(hass, HOT_WATER_TANK_ENTITY_ID)
    assert (state.attributes[ATTR_MIN_TEMP], state.attributes[ATTR_MAX_TEMP]) == DEFAULT_LIMITS

    await config_entry.runtime_data.async_refresh()

    state = get_state(hass, HOT_WATER_TANK_ENTITY_ID)
    assert (state.attributes[ATTR_MIN_TEMP], state.attributes[ATTR_MAX_TEMP]) == (0, 52)


async def test_buffer_tank_sensor_not_in_use(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a buffer tank uses the other temperature if the control unit reports the top sensor as not in use."""
    fake_api.message_ids = {"APPL.CtrlAppl.sParam.bufferTank[0].topTemp.state.msgId": 10}
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    state: State = get_state(hass, BUFFER_TANK_1_ENTITY_ID)
    # This is the bottom temperature, the top temperature 45.67 is not in use.
    assert (state.state, state.attributes[ATTR_CURRENT_TEMPERATURE]) == (STATE_OFF, 15.7)
