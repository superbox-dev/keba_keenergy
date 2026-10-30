# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the water heater entities."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any

import pytest
from homeassistant.components.water_heater import ATTR_MAX_TEMP
from homeassistant.components.water_heater import ATTR_MIN_TEMP
from homeassistant.components.water_heater import ATTR_OPERATION_MODE
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
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.keba_keenergy.const import FLASH_WRITE_DELAY
from tests import get_platform_states
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_RESPONSE
from tests.api_data import SINGLE_DEVICE_DATA_RESPONSE
from tests.api_data import SINGLE_DEVICE_FIXED_DATA_RESPONSE
from tests.api_data import SINGLE_DEVICE_RESPONSE
from tests.api_data import get_multiple_devices_fixed_data_response
from tests.api_data import get_single_device_data_response
from tests.api_data import update_response
from tests.test_water_heater_data import ENTITY_ID
from tests.test_water_heater_data import ENTITY_ID_1
from tests.test_water_heater_data import ENTITY_ID_2
from tests.test_water_heater_data import ENTITY_ID_3
from tests.test_water_heater_data import ENTITY_ID_4

if TYPE_CHECKING:
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    ("response", "entities"),
    [
        (
            [
                SINGLE_DEVICE_RESPONSE,
                SINGLE_DEVICE_FIXED_DATA_RESPONSE,
                SINGLE_DEVICE_DATA_RESPONSE,
            ],
            [ENTITY_ID, ENTITY_ID_3],
        ),
        (
            [
                MULTIPLE_DEVICES_RESPONSE,
                get_multiple_devices_fixed_data_response(),
                MULTIPLE_DEVICES_DATA_RESPONSE,
            ],
            [ENTITY_ID_1, ENTITY_ID_2, ENTITY_ID_4],
        ),
    ],
    ids=["single_device", "multiple_devices"],
)
async def test_water_heater_entities(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    response: list[list[dict[str, Any]]],
    entities: list[str],
) -> None:
    """Test that the water heater entities are created for the tanks."""
    fake_api.responses = [*response]
    await fake_api.setup_integration()

    for entity in entities:
        assert isinstance(hass.states.get(entity), State)


@pytest.mark.parametrize("language", ["en", "de"], indirect=True, ids=["en", "de"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_water_heater(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all water heater entities."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.WATER_HEATER):
        assert state == snapshot(name=state.entity_id)


@pytest.mark.parametrize(
    ("entity_id", "response", "expected"),
    [
        (
            "water_heater.keba_keenergy_12345678_1",
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "0"}]',
        ),
        (
            "water_heater.keba_keenergy_12345678_buffer_tank_1",
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "0"}]',
        ),
    ],
    ids=["hot_water_tank", "buffer_tank"],
)
async def test_turn_off(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    response: list[dict[str, Any]],
    expected: str,
) -> None:
    """Test turning off a tank."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        response,
        # Read the API after the action call.
        response,
    ]
    await fake_api.setup_integration()

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
    ids=["hot_water_tank", "buffer_tank"],
)
async def test_turn_on(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    expected: str,
) -> None:
    """Test turning on a tank."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

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
    ("operation_mode", "response", "expected"),
    [
        (
            STATE_ECO,
            MULTIPLE_DEVICES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "1"}]',
        ),
        (
            STATE_PERFORMANCE,
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "3"}]',
        ),
        (
            STATE_OFF,
            MULTIPLE_DEVICES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "0"}]',
        ),
        (
            STATE_HEAT_PUMP,
            MULTIPLE_DEVICES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "2"}]',
        ),
    ],
    ids=["eco", "performance", "off", "heat_pump"],
)
async def test_set_operation_mode_hot_water_tank(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    operation_mode: str,
    response: list[dict[str, Any]],
    expected: str,
) -> None:
    """Test setting the operation mode of a hot water tank."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        response,
        # Read the API after the action call.
        response,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_OPERATION_MODE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_1,
            ATTR_OPERATION_MODE: operation_mode,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("operation_mode", "response", "expected"),
    [
        (
            STATE_PERFORMANCE,
            MULTIPLE_DEVICES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "2"}]',
        ),
        (
            STATE_OFF,
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "0"}]',
        ),
        (
            STATE_HEAT_PUMP,
            MULTIPLE_DEVICES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "1"}]',
        ),
    ],
    ids=["performance", "off", "heat_pump"],
)
async def test_set_operation_mode_buffer_tank(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    operation_mode: str,
    response: list[dict[str, Any]],
    expected: str,
) -> None:
    """Test setting the operation mode of a buffer tank."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        response,
        # Read the API after the action call.
        response,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_OPERATION_MODE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID_4,
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
    ids=["hot_water_tank"],
)
async def test_set_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: int,
    expected: str,
) -> None:
    """Test setting the target temperature of a hot water tank."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_TEMPERATURE: value,
        },
        blocking=True,
    )

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
    await hass.async_block_till_done()

    fake_api.assert_called_write_with(expected)


async def test_set_temperature_debounced(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that quick target temperature changes are shown at once and written once, with the last value."""
    fake_api.responses = [
        SINGLE_DEVICE_RESPONSE,
        SINGLE_DEVICE_FIXED_DATA_RESPONSE,
        get_single_device_data_response(hot_water_tank_target_temperature="51"),
        # Read the API after the update of the entity.
        get_single_device_data_response(hot_water_tank_target_temperature="51"),
    ]
    await fake_api.setup_integration()

    temperatures: tuple[float, ...] = (45.0, 44.0)

    for temperature in temperatures:
        await hass.services.async_call(
            domain=WATER_HEATER_DOMAIN,
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
        '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", "value": "44.0"}]',
    ]


@pytest.mark.parametrize(
    ("entity_id", "service", "response"),
    [
        (ENTITY_ID_2, SERVICE_TURN_OFF, MULTIPLE_DEVICES_DATA_RESPONSE),
        (ENTITY_ID_1, SERVICE_TURN_ON, MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE),
        (ENTITY_ID_4, SERVICE_TURN_OFF, MULTIPLE_DEVICES_DATA_RESPONSE),
        (ENTITY_ID_4, SERVICE_TURN_ON, MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE),
    ],
    ids=["hot_water_tank_2_turn_off", "hot_water_tank_1_turn_on", "buffer_tank_turn_off", "buffer_tank_turn_on"],
)
async def test_unchanged_state(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    service: str,
    response: list[dict[str, Any]],
) -> None:
    """Test that a tank is not written if it is already turned on or off."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        response,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=service,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    assert fake_api.write_requests() == []


async def test_set_unchanged_target_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the current target temperature of a hot water tank is not written again."""
    fake_api.responses = [
        SINGLE_DEVICE_RESPONSE,
        SINGLE_DEVICE_FIXED_DATA_RESPONSE,
        get_single_device_data_response(hot_water_tank_target_temperature="51"),
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: ENTITY_ID,
            ATTR_TEMPERATURE: 51,
        },
        blocking=True,
    )

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=FLASH_WRITE_DELAY))
    await hass.async_block_till_done()

    assert fake_api.write_requests() == []


async def test_limits_after_update(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a hot water tank uses the limits from the API once an update provides them."""
    fake_api.responses = [
        SINGLE_DEVICE_RESPONSE,
        SINGLE_DEVICE_FIXED_DATA_RESPONSE,
        update_response(
            get_single_device_data_response(),
            "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value",
            attributes={},
        ),
        get_single_device_data_response(),
    ]
    await fake_api.setup_integration()

    state: State | None = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)
    assert (state.attributes[ATTR_MIN_TEMP], state.attributes[ATTR_MAX_TEMP]) != (0, 52)

    await config_entry.runtime_data.async_refresh()

    state = hass.states.get(ENTITY_ID)
    assert isinstance(state, State)
    assert (state.attributes[ATTR_MIN_TEMP], state.attributes[ATTR_MAX_TEMP]) == (0, 52)


async def test_buffer_tank_sensor_not_in_use(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a buffer tank uses the other temperature if the control unit reports the top sensor as not in use."""
    fake_api.message_ids = {"APPL.CtrlAppl.sParam.bufferTank[0].topTemp.state.msgId": 10}
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    state: State | None = hass.states.get("water_heater.keba_keenergy_12345678_buffer_tank_1")
    assert isinstance(state, State)
    # This is the bottom temperature, the top temperature 45.67 is not in use.
    assert (state.state, state.attributes["current_temperature"]) == (STATE_OFF, 15.7)
