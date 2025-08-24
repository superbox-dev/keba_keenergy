from unittest.mock import patch

import pytest
from aiohttp import ClientError
from homeassistant.components.homeassistant import SERVICE_UPDATE_ENTITY
from homeassistant.components.homeassistant.const import DOMAIN as HA_DOMAIN
from homeassistant.components.number import ATTR_VALUE
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number.const import SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.setup import async_setup_component
from keba_keenergy_api.api import KebaKeEnergyAPI
from keba_keenergy_api.error import APIError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_DATA_UPDATED_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.conftest import FakeKebaKeEnergyAPI


async def test_entity_update(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test updating entity using homeassistant.update_entity."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_UPDATED_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await async_setup_component(hass, HA_DOMAIN, {})
    await setup_integration(hass, config_entry)

    entity_id: str = "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1"
    heat_circuit_operating_mode_1: State | None = hass.states.get(entity_id)
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.state == STATE_OFF

    await hass.services.async_call(
        HA_DOMAIN,
        SERVICE_UPDATE_ENTITY,
        {
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    heat_circuit_operating_mode_1 = hass.states.get(
        "sensor.keba_keenergy_12345678_heat_circuit_operating_mode_1",
    )
    assert isinstance(heat_circuit_operating_mode_1, State)
    assert heat_circuit_operating_mode_1.state == "auto"


@pytest.mark.parametrize(
    ("side_effect", "expected_error"),
    [
        (
            APIError("mocked api error"),
            "Failed to update number.keba_keenergy_12345678_hot_water_tank_min_temperature_1 to 10.0: "
            "mocked api error",
        ),
        (
            ClientError("mocked client error"),
            "Failed to update number.keba_keenergy_12345678_hot_water_tank_min_temperature_1 to 10.0: "
            "mocked client error",
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
    """Test updating entity using homeassistant.update_entity."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    entity_id: str = "number.keba_keenergy_12345678_hot_water_tank_min_temperature_1"
    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    with patch.object(KebaKeEnergyAPI, "write_data", side_effect=side_effect):
        with pytest.raises(HomeAssistantError) as error:
            await hass.services.async_call(
                NUMBER_DOMAIN,
                SERVICE_SET_VALUE,
                {
                    ATTR_ENTITY_ID: entity_id,
                    ATTR_VALUE: 10,
                },
                blocking=True,
            )

        assert str(error.value) == expected_error
