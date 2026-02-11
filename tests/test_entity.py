from unittest.mock import patch

import pytest
from homeassistant.components.homeassistant import SERVICE_UPDATE_ENTITY
from homeassistant.components.homeassistant.const import DOMAIN as HA_DOMAIN
from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.translation import async_get_translations
from homeassistant.setup import async_setup_component
from keba_keenergy_api.api import KebaKeEnergyAPI
from keba_keenergy_api.error import APIError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.keba_keenergy.const import DOMAIN
from tests import setup_integration
from tests.api_data import ENTITY_UPDATED_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI


async def test_entity_update(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        ENTITY_UPDATED_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await async_setup_component(hass, HA_DOMAIN, {})
    await setup_integration(hass, config_entry)

    entity_id: str = "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_2"
    heat_circuit_operating_mode_1: State | None = hass.states.get(entity_id)
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.state == STATE_OFF

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


@pytest.mark.parametrize(
    ("side_effect", "expected_error"),
    [
        (
            APIError("mocked api error"),
            "An error occurred while communicate with the API: mocked api error",
        ),
        (
            APIError("mocked client error"),
            "An error occurred while communicate with the API: mocked client error",
        ),
    ],
)
async def test_entity_update_failed(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    side_effect: Exception,
    expected_error: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    entity_id: str = "select.keba_keenergy_12345678_buffer_tank_operating_mode_1"
    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    with (
        patch.object(KebaKeEnergyAPI, "write_data", side_effect=side_effect),
        pytest.raises(HomeAssistantError, match=expected_error),
    ):
        await hass.services.async_call(
            domain=SELECT_DOMAIN,
            service=SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_OPTION: "on",
            },
            blocking=True,
        )

    translations = await async_get_translations(
        hass,
        "de",
        "exceptions",
        [DOMAIN],
    )

    assert (
        translations[f"component.{DOMAIN}.exceptions.communication_error.message"]
        == "Bei der Kommunikation mit der API ist ein Fehler aufgetreten: {error}"
    )
