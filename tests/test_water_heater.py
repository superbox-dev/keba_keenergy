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
from pytest_homeassistant.common import snapshot_platform

from tests import fire_debounced_writes
from tests import get_state
from tests import next_update
from tests import replace_attributes
from tests import replace_values
from tests import set_target_temperature
from tests.const import NOW
from tests.const import OTHER_MODES_VALUES
from tests.test_water_heater_data import BUFFER_TANK
from tests.test_water_heater_data import BUFFER_TANK_1_ENTITY_ID
from tests.test_water_heater_data import DEFAULT_LIMITS
from tests.test_water_heater_data import HOT_WATER_TANK
from tests.test_water_heater_data import HOT_WATER_TANK_1_ENTITY_ID
from tests.test_water_heater_data import HOT_WATER_TANK_2_ENTITY_ID
from tests.test_water_heater_data import HOT_WATER_TANK_ENTITY_ID
from tests.test_water_heater_data import get_operating_mode_write

if TYPE_CHECKING:
    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
    from homeassistant.helpers import entity_registry as er
    from pytest_homeassistant.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI

pytestmark = pytest.mark.freeze_time(NOW)


@pytest.mark.parametrize("language", ["de", "en"], ids=["de", "en"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_water_heater(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    language: str,
) -> None:
    """Test the states of all water heater entities."""
    hass.config.language = language
    fake_api.load_device("multiple_devices")
    fake_api.platforms = [Platform.WATER_HEATER]
    await fake_api.setup_integration()

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.parametrize(
    ("service_call", "values", "expected_writes"),
    [
        (
            (SERVICE_TURN_OFF, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID}),
            OTHER_MODES_VALUES,
            [get_operating_mode_write(HOT_WATER_TANK, 0)],
        ),
        ((SERVICE_TURN_OFF, {ATTR_ENTITY_ID: HOT_WATER_TANK_2_ENTITY_ID}), {}, []),
        (
            (SERVICE_TURN_OFF, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID}),
            OTHER_MODES_VALUES,
            [get_operating_mode_write(BUFFER_TANK, 0)],
        ),
        ((SERVICE_TURN_OFF, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID}), {}, []),
        (
            (SERVICE_TURN_ON, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID}),
            {},
            [get_operating_mode_write(HOT_WATER_TANK, 2)],
        ),
        (
            (SERVICE_TURN_ON, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID}),
            OTHER_MODES_VALUES,
            [],
        ),
        (
            (SERVICE_TURN_ON, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID}),
            {},
            [get_operating_mode_write(BUFFER_TANK, 1)],
        ),
        ((SERVICE_TURN_ON, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID}), OTHER_MODES_VALUES, []),
        (
            (SERVICE_SET_OPERATION_MODE, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_ECO}),
            {},
            [get_operating_mode_write(HOT_WATER_TANK, 1)],
        ),
        (
            (
                SERVICE_SET_OPERATION_MODE,
                {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_PERFORMANCE},
            ),
            OTHER_MODES_VALUES,
            [get_operating_mode_write(HOT_WATER_TANK, 3)],
        ),
        (
            (SERVICE_SET_OPERATION_MODE, {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_OFF}),
            {},
            [get_operating_mode_write(HOT_WATER_TANK, 0)],
        ),
        (
            (
                SERVICE_SET_OPERATION_MODE,
                {ATTR_ENTITY_ID: HOT_WATER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_HEAT_PUMP},
            ),
            {},
            [get_operating_mode_write(HOT_WATER_TANK, 2)],
        ),
        (
            (
                SERVICE_SET_OPERATION_MODE,
                {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_PERFORMANCE},
            ),
            {},
            [get_operating_mode_write(BUFFER_TANK, 2)],
        ),
        (
            (SERVICE_SET_OPERATION_MODE, {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_OFF}),
            OTHER_MODES_VALUES,
            [get_operating_mode_write(BUFFER_TANK, 0)],
        ),
        (
            (
                SERVICE_SET_OPERATION_MODE,
                {ATTR_ENTITY_ID: BUFFER_TANK_1_ENTITY_ID, ATTR_OPERATION_MODE: STATE_HEAT_PUMP},
            ),
            {},
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
    values: dict[str, str],
    expected_writes: list[str],
) -> None:
    """Test turning on and off and setting the operation mode of a tank, the current mode is not written again."""
    fake_api.load_device("multiple_devices")
    fake_api.data = replace_values(fake_api.data, values)
    await fake_api.setup_integration()

    service, service_data = service_call
    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=service,
        service_data=service_data,
        blocking=True,
    )

    assert fake_api.write_requests() == expected_writes


@pytest.mark.usefixtures("init_integration")
async def test_set_temperature(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test setting the target temperature of a hot water tank."""
    await set_target_temperature(hass, HOT_WATER_TANK_1_ENTITY_ID, 45)

    await fire_debounced_writes(hass, freezer)

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", "value": "45.0"}]',
    ]


async def test_set_temperature_debounced(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that quick target temperature changes are shown at once and written once, with the last value."""
    fake_api.load_device("single_device")
    fake_api.responses = fake_api.setup_responses(
        fake_api.data,
        # Read the API after the update of the entity.
        fake_api.data,
    )
    await fake_api.setup_integration()

    temperatures: tuple[float, ...] = (45.0, 44.0)

    for temperature in temperatures:
        await set_target_temperature(hass, HOT_WATER_TANK_ENTITY_ID, temperature)

    await async_update_entity(hass, HOT_WATER_TANK_ENTITY_ID)

    state: State = get_state(hass, HOT_WATER_TANK_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == temperatures[-1]
    assert fake_api.write_requests() == []

    await fire_debounced_writes(hass, freezer)

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", "value": "44.0"}]',
    ]


async def test_set_unchanged_target_temperature(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the current target temperature of a hot water tank is not written again."""
    fake_api.load_device("single_device")
    await fake_api.setup_integration()

    await set_target_temperature(hass, HOT_WATER_TANK_ENTITY_ID, 51)

    await fire_debounced_writes(hass, freezer)

    assert fake_api.write_requests() == []


async def test_limits_after_update(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a hot water tank uses the limits from the API once an update provides them."""
    fake_api.load_device("single_device")
    fake_api.responses = fake_api.setup_responses(
        replace_attributes(fake_api.data, "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", {}),
        fake_api.data,
    )
    await fake_api.setup_integration()

    state: State = get_state(hass, HOT_WATER_TANK_ENTITY_ID)
    assert (state.attributes[ATTR_MIN_TEMP], state.attributes[ATTR_MAX_TEMP]) == DEFAULT_LIMITS

    await next_update(hass, freezer)

    state = get_state(hass, HOT_WATER_TANK_ENTITY_ID)
    assert (state.attributes[ATTR_MIN_TEMP], state.attributes[ATTR_MAX_TEMP]) == (0, 52)


async def test_buffer_tank_sensor_not_in_use(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a buffer tank uses the other temperature if the control unit reports the top sensor as not in use."""
    fake_api.load_device("multiple_devices")
    fake_api.message_ids = {"APPL.CtrlAppl.sParam.bufferTank[0].topTemp.state.msgId": 10}
    await fake_api.setup_integration()

    state: State = get_state(hass, BUFFER_TANK_1_ENTITY_ID)
    # This is the bottom temperature, the top temperature 45.67 is not in use.
    assert (state.state, state.attributes[ATTR_CURRENT_TEMPERATURE]) == (STATE_OFF, 15.7)
