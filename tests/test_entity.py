# Copyright 2026 Michael Hacker
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
from tests import init_translations
from tests.api_data import ENTITY_UPDATED_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from tests.conftest import FakeKebaKeEnergyAPI


async def test_entity_update(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test writing a value of an entity."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        ENTITY_UPDATED_DATA_RESPONSE,
    ]
    await async_setup_component(hass, HA_DOMAIN, {})
    await fake_api.setup_integration()

    entity_id: str = "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_2"
    heat_circuit_operating_mode_1: State | None = hass.states.get(entity_id)
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.state == "auto"

    await hass.services.async_call(
        domain=HA_DOMAIN,
        service=SERVICE_UPDATE_ENTITY,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    heat_circuit_operating_mode_1 = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1",
    )
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.state == "night"


async def test_entity_update_failed(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the translated error if writing a value of an entity fails."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    fake_api.write_status = HTTPStatus.BAD_REQUEST
    hass.config.language = "de"
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="exceptions")

    with pytest.raises(HomeAssistantError, match="An error occurred while communicating with the API: ") as error:
        await hass.services.async_call(
            domain=SELECT_DOMAIN,
            service=SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: "select.keba_keenergy_12345678_buffer_tank_operating_mode_1",
                ATTR_OPTION: "on",
            },
            blocking=True,
        )

    assert error.value.translation_key == "communication_error"
    assert (
        translations["component.keba_keenergy.exceptions.communication_error.message"]
        == "Bei der Kommunikation mit der API ist ein Fehler aufgetreten: {error}"
    )


@pytest.mark.parametrize(
    ("system_name", "expected_manufacturer"),
    [
        ("KeEnergy.MTec", "M-TEC"),
        ("Bartl 4.0", "ino"),
        ("KeEnergy", None),
    ],
)
async def test_heat_pump_manufacturer(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    system_name: str,
    expected_manufacturer: str | None,
) -> None:
    """Test the manufacturer of the heat pump device, detected from the system name."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    fake_api.system_name = system_name
    await fake_api.setup_integration()

    manufacturers: list[str | None] = [
        device.manufacturer
        for device in dr.async_entries_for_config_entry(dr.async_get(hass), fake_api.config_entry.entry_id)
        if (DOMAIN, "12345678_heat_pump") in device.identifiers
    ]
    assert manufacturers == [expected_manufacturer]
