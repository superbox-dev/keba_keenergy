from __future__ import annotations

import json
from datetime import timedelta
from typing import Any
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.error import APIError
from keba_keenergy_api.error import AuthenticationError
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.coordinator import KebaKeEnergyDataUpdateCoordinator
from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import HEATING_CURVE_NAMES_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_3_1
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_3_2
from tests.api_data import SYSTEM_BUFFER_TANK_NUMBERS
from tests.api_data import SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS
from tests.api_data import SYSTEM_HEAT_CIRCUIT_NUMBERS
from tests.api_data import SYSTEM_HEAT_PUMP_NUMBERS
from tests.api_data import SYSTEM_HOT_WATER_TANK_NUMBERS
from tests.api_data import SYSTEM_SOLAR_CIRCUIT_NUMBERS
from tests.api_data import SYSTEM_SWITCH_VALVE_NUMBERS
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from aiohttp import ClientSession
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion
    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    ("side_effect", "raise_exception", "expected_translation_key", "expected_error"),
    [
        (APIError("boom"), UpdateFailed, "communication_error", {"error": "boom"}),
        (AuthenticationError("boom"), ConfigEntryAuthFailed, "authentication_error", None),
    ],
)
async def test_async_update_data_api_error_raises_update_failed(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    side_effect: Exception,
    raise_exception: type[HomeAssistantError],
    expected_translation_key: str,
    expected_error: dict[str, Any] | None,
) -> None:
    session: ClientSession = async_get_clientsession(hass, verify_ssl=False)

    coordinator: KebaKeEnergyDataUpdateCoordinator = KebaKeEnergyDataUpdateCoordinator(
        hass,
        config_entry,
        host="10.0.0.100",
        username=None,
        password=None,
        ssl=False,
        session=session,
    )

    with (
        patch.object(
            coordinator.api,
            "read_data",
            new=AsyncMock(side_effect=side_effect),
        ),
        pytest.raises(raise_exception) as error,
    ):
        await coordinator._async_update_data()

    assert error.value.translation_domain == DOMAIN
    assert error.value.translation_key == expected_translation_key
    assert error.value.translation_placeholders == expected_error


@pytest.mark.parametrize(
    "config_entry",
    [
        {
            "options": {
                "scan_interval": 20,
                "scan_interval_tick_system": 1,
                "scan_interval_tick_heat_pump": 1,
                "scan_interval_tick_heat_circuit": 2,
                "scan_interval_tick_solar_circuit": 1,
                "scan_interval_tick_hot_water_tank": 1,
                "scan_interval_tick_buffer_tank": 1,
                "scan_interval_tick_switch_valve": 1,
                "scan_interval_tick_external_heat_source": 1,
            },
        },
    ],
    indirect=True,
)
async def test_update_interval_ticks(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    fake_api.responses = [
        [
            json.loads(SYSTEM_HEAT_PUMP_NUMBERS % "1"),
            json.loads(SYSTEM_HEAT_CIRCUIT_NUMBERS % "2"),
            json.loads(SYSTEM_SOLAR_CIRCUIT_NUMBERS % "0"),
            json.loads(SYSTEM_BUFFER_TANK_NUMBERS % "2"),
            json.loads(SYSTEM_HOT_WATER_TANK_NUMBERS % "2"),
            json.loads(SYSTEM_EXTERNAL_HEAT_SOURCE_NUMBERS % "2"),
            json.loads(SYSTEM_SWITCH_VALVE_NUMBERS % "2"),
        ],
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_3_2,
        *HEATING_CURVES_RESPONSE_1_1,
        MULTIPLE_POSITION_DATA_RESPONSE_3_2,
        *HEATING_CURVES_RESPONSE_1_1,
        MULTIPLE_POSITION_DATA_RESPONSE_3_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]

    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    coordinator: KebaKeEnergyDataUpdateCoordinator = config_entry.runtime_data

    assert not coordinator.request_data_groups.get(SectionPrefix.SOLAR_CIRCUIT)
    assert coordinator._tick_counter == 1

    assert coordinator.data == snapshot

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
    await coordinator.async_request_refresh()
    await hass.async_block_till_done()

    assert coordinator._tick_counter == 2

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
    await coordinator.async_request_refresh()
    await hass.async_block_till_done()

    assert coordinator._tick_counter == 3

    assert coordinator.data == snapshot
