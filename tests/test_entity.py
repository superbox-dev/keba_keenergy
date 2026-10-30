# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the base entity."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from homeassistant.components.homeassistant import SERVICE_UPDATE_ENTITY
from homeassistant.components.homeassistant.const import DOMAIN as HA_DOMAIN
from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.setup import async_setup_component

from custom_components.keba_keenergy.const import DOMAIN
from tests import get_state
from tests.api_data import ENTITY_UPDATED_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import get_multiple_devices_responses
from tests.test_issues_data import WRITE_COUNT_ENTITY_ID

if TYPE_CHECKING:
    from tests.conftest import FakeKebaKeEnergyAPI


async def test_entity_update(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test writing a value of an entity."""
    fake_api.responses = get_multiple_devices_responses(
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the action call.
        ENTITY_UPDATED_DATA_RESPONSE,
    )
    await async_setup_component(hass, HA_DOMAIN, {})
    await fake_api.setup_integration()

    entity_id: str = "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_2"
    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)
    assert state.state == "auto"

    await hass.services.async_call(
        domain=HA_DOMAIN,
        service=SERVICE_UPDATE_ENTITY,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    # The update of one entity updates all entities of the coordinator.
    state = hass.states.get("sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1")
    assert isinstance(state, State)
    assert state.state == "night"


async def test_entity_update_failed(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that an entity keeps its state and raises a translated error if writing a value fails, uncounted."""
    entity_id: str = "select.keba_keenergy_12345678_buffer_tank_operating_mode_1"
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    fake_api.write_status = HTTPStatus.BAD_REQUEST
    await fake_api.setup_integration()

    with pytest.raises(HomeAssistantError, match="An error occurred while communicating with the API: ") as error:
        await hass.services.async_call(
            domain=SELECT_DOMAIN,
            service=SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_OPTION: "on",
            },
            blocking=True,
        )

    state: State | None = hass.states.get(entity_id)

    assert error.value.translation_key == "communication_error"
    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "1"}]',
    ]
    assert isinstance(state, State)
    assert state.state == "off"
    # A failed write does not change the flash memory, so it is not counted.
    assert get_state(hass, WRITE_COUNT_ENTITY_ID) == "0"


@pytest.mark.parametrize(
    ("system_name", "expected_manufacturer"),
    [
        ("KeEnergy.MTec", "M-TEC"),
        ("Bartl 4.0", "ino"),
        ("KeEnergy", None),
    ],
    ids=["m_tec", "ino", "unknown"],
)
async def test_heat_pump_manufacturer(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    system_name: str,
    expected_manufacturer: str | None,
) -> None:
    """Test the manufacturer of the heat pump device, detected from the system name."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    fake_api.system_name = system_name
    await fake_api.setup_integration()

    manufacturers: list[str | None] = [
        device.manufacturer
        for device in dr.async_entries_for_config_entry(dr.async_get(hass), fake_api.config_entry.entry_id)
        if (DOMAIN, "12345678_heat_pump") in device.identifiers
    ]
    assert manufacturers == [expected_manufacturer]


async def test_entities_keep_their_state_if_queued_updates_failed(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that entities keep their states if writes fail, which waited for each other."""
    entity_id_1: str = "select.keba_keenergy_12345678_buffer_tank_operating_mode_1"
    entity_id_2: str = "select.keba_keenergy_12345678_buffer_tank_operating_mode_2"
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    fake_api.write_status = HTTPStatus.BAD_REQUEST
    await fake_api.setup_integration()

    with pytest.raises(HomeAssistantError, match="400 Bad Request"):
        # The entities write at the same time, so the second write waits for the first one.
        await hass.services.async_call(
            domain=SELECT_DOMAIN,
            service=SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: [entity_id_1, entity_id_2],
                ATTR_OPTION: "heat_up",
            },
            blocking=True,
        )

    await hass.async_block_till_done()

    state_1: State | None = hass.states.get(entity_id_1)
    state_2: State | None = hass.states.get(entity_id_2)

    # Home Assistant does not define the order of the entities of one action call.
    assert sorted(fake_api.write_requests()) == [
        '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.operatingMode", "value": "2"}]',
        '[{"name": "APPL.CtrlAppl.sParam.bufferTank[1].param.operatingMode", "value": "2"}]',
    ]
    assert isinstance(state_1, State)
    assert isinstance(state_2, State)
    assert (state_1.state, state_2.state) == ("off", "on")
