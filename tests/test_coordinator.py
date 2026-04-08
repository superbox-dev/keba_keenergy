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

    assert coordinator.data == {
        "system": {
            "outdoor_temperature": {"value": 20.5, "attributes": {"upper_limit": "100", "lower_limit": "-100"}},
            "operating_mode": {"value": "auto_heat", "attributes": {"lower_limit": "-1", "upper_limit": "4"}},
            "cpu_usage": {"value": 27.0, "attributes": {}},
            "webview_cpu_usage": {"value": 34.0, "attributes": {}},
            "webserver_cpu_usage": {"value": 67.0, "attributes": {}},
            "control_cpu_usage": {"value": 7.0, "attributes": {}},
            "ram_usage": {"value": 6432, "attributes": {}},
            "free_ram": {"value": 100060, "attributes": {}},
        },
        "buffer_tank": {
            "current_top_temperature": [
                {"value": 45.67, "attributes": {"upper_limit": "90", "lower_limit": "5"}},
                {"value": 35.67, "attributes": {"upper_limit": "90", "lower_limit": "5"}},
            ],
            "current_bottom_temperature": [
                {"value": 15.67, "attributes": {"upper_limit": "90", "lower_limit": "5"}},
                {"value": 25.67, "attributes": {"upper_limit": "90", "lower_limit": "5"}},
            ],
            "operating_mode": [
                {"value": "off", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
                {"value": "on", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
            ],
            "standby_temperature": [
                {"value": 10.0, "attributes": {"upper_limit": "90", "lower_limit": "0"}},
                {"value": 11.0, "attributes": {"upper_limit": "90", "lower_limit": "0"}},
            ],
            "target_temperature": [
                {"value": 44.0, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 43.0, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "heat_request": [{"value": "off", "attributes": {}}, {"value": "on", "attributes": {}}],
            "cool_request": [{"value": "on", "attributes": {}}, {"value": "off", "attributes": {}}],
        },
        "hot_water_tank": {
            "heat_request": [{"value": "off", "attributes": {}}, {"value": "on", "attributes": {}}],
            "hot_water_flow": [{"value": "off", "attributes": {}}, {"value": "on", "attributes": {}}],
            "fresh_water_module_temperature": [
                {"value": 51.23, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 51.23, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "target_temperature": [
                {"value": 51.0, "attributes": {"upper_limit": "52", "lower_limit": "0"}},
                {"value": 51.0, "attributes": {"upper_limit": "52", "lower_limit": "0"}},
            ],
            "standby_temperature": [
                {"value": 32.5, "attributes": {"upper_limit": "52", "lower_limit": "0"}},
                {"value": 32.5, "attributes": {"upper_limit": "52", "lower_limit": "0"}},
            ],
            "operating_mode": [
                {"value": "heat_up", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
                {"value": "off", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
            ],
            "current_temperature": [
                {"value": 47.7, "attributes": {"upper_limit": "90", "lower_limit": "20"}},
                {"value": 47.7, "attributes": {"upper_limit": "90", "lower_limit": "20"}},
            ],
            "circulation_return_temperature": [
                {"value": 30.45, "attributes": {"upper_limit": "100", "lower_limit": "-100"}},
                {"value": 27.45, "attributes": {"upper_limit": "100", "lower_limit": "-100"}},
            ],
            "circulation_pump_state": [{"value": "on", "attributes": {}}, {"value": "off", "attributes": {}}],
        },
        "heat_pump": {
            "circulation_pump": [{"value": 0.0, "attributes": {"upper_limit": "1", "lower_limit": "0.0"}}],
            "source_pump_speed": [{"value": 0.45, "attributes": {"upper_limit": "1", "lower_limit": "0.0"}}],
            "compressor": [{"value": 0.0, "attributes": {"upper_limit": "1", "lower_limit": "0.0"}}],
            "compressor_night_speed": [{"value": 0.5, "attributes": {"upper_limit": "1", "lower_limit": "0.5"}}],
            "compressor_input_temperature": [{"value": 27.2, "attributes": {}}],
            "compressor_output_temperature": [{"value": 27.2, "attributes": {}}],
            "compressor_use_night_speed": [{"value": "on", "attributes": {}}],
            "condenser_temperature": [{"value": 31.51, "attributes": {"upper_limit": "200", "lower_limit": "0"}}],
            "vaporizer_temperature": [{"value": -4.56, "attributes": {}}],
            "target_overheating": [{"value": 5.5, "attributes": {}}],
            "current_overheating": [{"value": 18.68, "attributes": {}}],
            "expansion_valve_position": [{"value": 20, "attributes": {}}],
            "heat_request": [{"value": "off", "attributes": {}}],
            "high_pressure": [{"value": 15.62, "attributes": {}}],
            "flow_temperature": [{"value": 24.8, "attributes": {}}],
            "low_pressure": [{"value": 15.35, "attributes": {}}],
            "name": [{"value": "WPS26", "attributes": {}}],
            "return_flow_temperature": [{"value": 23.9, "attributes": {}}],
            "source_input_temperature": [{"value": 25.7, "attributes": {}}],
            "source_output_temperature": [{"value": 24.9, "attributes": {}}],
            "state": [{"value": "standby", "attributes": {"upper_limit": "32767", "lower_limit": "0"}}],
            "substate": [{"value": "oil_preheating", "attributes": {"upper_limit": "32767", "lower_limit": "0"}}],
            "compressor_power": [{"value": 5.52, "attributes": {}}],
            "heating_power": [{"value": 3.22, "attributes": {}}],
            "hot_water_power": [{"value": 2.77, "attributes": {}}],
            "cop": [{"value": 2.55, "attributes": {}}],
            "heating_energy": [{"value": 8.43, "attributes": {}}],
            "heating_energy_consumption": [{"value": 7.33, "attributes": {}}],
            "heating_spf": [{"value": 3.32, "attributes": {}}],
            "cooling_energy": [{"value": 7.21, "attributes": {}}],
            "cooling_energy_consumption": [{"value": 8.72, "attributes": {}}],
            "cooling_spf": [{"value": 4.22, "attributes": {}}],
            "hot_water_energy": [{"value": 7.86, "attributes": {}}],
            "hot_water_energy_consumption": [{"value": 2.77, "attributes": {}}],
            "hot_water_spf": [{"value": 2.5, "attributes": {}}],
            "total_thermal_energy": [{"value": 8.22, "attributes": {}}],
            "total_energy_consumption": [{"value": 5.21, "attributes": {}}],
            "total_spf": [{"value": 2.43, "attributes": {}}],
            "operating_time": [{"value": 3809028, "attributes": {}}],
            "max_runtime": [{"value": 602403, "attributes": {}}],
            "activation_counter": [{"value": 477, "attributes": {}}],
            "has_compressor_failure": [{"value": "off", "attributes": {}}],
            "has_source_failure": [{"value": "off", "attributes": {}}],
            "has_source_actuator_failure": [{"value": "off", "attributes": {}}],
            "has_three_phase_failure": [{"value": "off", "attributes": {}}],
            "has_source_pressure_failure": [{"value": "off", "attributes": {}}],
            "has_vfd_failure": [{"value": "off", "attributes": {}}],
        },
        "heat_circuit": {
            "room_temperature": [
                {"value": 22.42, "attributes": {"upper_limit": "80", "lower_limit": "0"}},
                {"value": 22.42, "attributes": {"upper_limit": "80", "lower_limit": "0"}},
            ],
            "room_humidity": [
                {"value": 53.0, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 53.0, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "dew_point": [
                {"value": 13.1, "attributes": {"upper_limit": "50.0", "lower_limit": "-20.0"}},
                {"value": 13.1, "attributes": {"upper_limit": "50.0", "lower_limit": "-20.0"}},
            ],
            "flow_temperature_setpoint": [
                {"value": 26.55, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 26.55, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "flow_temperature": [
                {"value": 24.34, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 24.34, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "return_flow_temperature": [
                {"value": 22.21, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 22.21, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "target_temperature_day": [
                {"value": 20.5, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
                {"value": 20.5, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
            ],
            "heating_limit_day": [
                {"value": 20.0, "attributes": {"upper_limit": "100", "lower_limit": "-20"}},
                {"value": 20.0, "attributes": {"upper_limit": "100", "lower_limit": "-20"}},
            ],
            "heat_request": [
                {"value": "on", "attributes": {"upper_limit": "6", "lower_limit": "0"}},
                {"value": "off", "attributes": {"upper_limit": "6", "lower_limit": "0"}},
            ],
            "cool_request": [
                {"value": "off", "attributes": {"upper_limit": "6", "lower_limit": "0"}},
                {"value": "on", "attributes": {"upper_limit": "6", "lower_limit": "0"}},
            ],
            "target_temperature_away": [
                {"value": 18.0, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
                {"value": 18.0, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
            ],
            "target_temperature_night": [
                {"value": 20.0, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
                {"value": 20.0, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
            ],
            "heating_limit_night": [
                {"value": 18.0, "attributes": {"upper_limit": "100", "lower_limit": "-20"}},
                {"value": 18.0, "attributes": {"upper_limit": "100", "lower_limit": "-20"}},
            ],
            "operating_mode": [
                {"value": "day", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
                {"value": "off", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
            ],
            "selected_target_temperature": [{"value": 20.0, "attributes": {}}, {"value": 20.0, "attributes": {}}],
            "target_temperature": [
                {"value": 20.5, "attributes": {"upper_limit": "90", "lower_limit": "10"}},
                {"value": 20.5, "attributes": {"upper_limit": "90", "lower_limit": "10"}},
            ],
            "target_temperature_offset": [
                {"value": 1.5, "attributes": {"upper_limit": "2.5", "lower_limit": "-2.5"}},
                {"value": 0.0, "attributes": {"upper_limit": "2.5", "lower_limit": "-2.5"}},
            ],
            "away_start_date": [
                {"value": 1769036400, "attributes": {"upper_limit": "86400", "lower_limit": "0"}},
                {"value": 1769036400, "attributes": {"upper_limit": "86400", "lower_limit": "0"}},
            ],
            "away_end_date": [
                {"value": 1769122799, "attributes": {"upper_limit": "86400", "lower_limit": "0"}},
                {"value": 1769122799, "attributes": {"upper_limit": "86400", "lower_limit": "0"}},
            ],
            "heating_curve_offset": [
                {"value": 1.5, "attributes": {"upper_limit": "10", "lower_limit": "-10"}},
                {"value": -1.5, "attributes": {"upper_limit": "10", "lower_limit": "-10"}},
            ],
            "heating_curve_slope": [
                {"value": 0.5, "attributes": {"upper_limit": "5", "lower_limit": "0"}},
                {"value": 0.6, "attributes": {"upper_limit": "5", "lower_limit": "0"}},
            ],
            "use_heating_curve": [{"value": "off", "attributes": {}}, {"value": "on", "attributes": {}}],
            "heating_curve": [
                {
                    "value": "HC6",
                    "attributes": {
                        "points": [
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                        ],
                    },
                },
                {
                    "value": "HC7",
                    "attributes": {
                        "points": [
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                        ],
                    },
                },
            ],
            "pump_speed": [
                {"value": 0.5, "attributes": {"upper_limit": "1", "lower_limit": "0"}},
                {"value": 0.5, "attributes": {"upper_limit": "1", "lower_limit": "0"}},
            ],
        },
        "solar_circuit": {},
        "external_heat_source": {
            "operating_mode": [
                {"value": "off", "attributes": {"upper_limit": "2", "lower_limit": "0"}},
                {"value": "on", "attributes": {"upper_limit": "2", "lower_limit": "0"}},
            ],
            "target_temperature": [
                {"value": 17.23, "attributes": {"upper_limit": "90", "lower_limit": "20"}},
                {"value": 17.23, "attributes": {"upper_limit": "90", "lower_limit": "20"}},
            ],
            "heat_request": [{"value": "on", "attributes": {}}, {"value": "on", "attributes": {}}],
            "operating_time": [{"value": 812999, "attributes": {}}, {"value": 812999, "attributes": {}}],
            "max_runtime": [{"value": 8129, "attributes": {}}, {"value": 8129, "attributes": {}}],
            "activation_counter": [{"value": 812, "attributes": {}}, {"value": 812, "attributes": {}}],
        },
        "switch_valve": {
            "position": [
                {"value": "neutral", "attributes": {"upper_limit": "2", "lower_limit": "0"}},
                {"value": "open", "attributes": {"upper_limit": "2", "lower_limit": "0"}},
            ],
        },
        "photovoltaic": {},
    }

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
    await coordinator.async_request_refresh()
    await hass.async_block_till_done()

    assert coordinator._tick_counter == 2

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
    await coordinator.async_request_refresh()
    await hass.async_block_till_done()

    assert coordinator._tick_counter == 3

    assert coordinator.data == {
        "system": {
            "outdoor_temperature": {"value": 20.5, "attributes": {"upper_limit": "100", "lower_limit": "-100"}},
            "operating_mode": {"value": "auto_heat", "attributes": {"lower_limit": "-1", "upper_limit": "4"}},
            "cpu_usage": {"value": 27.0, "attributes": {}},
            "webview_cpu_usage": {"value": 34.0, "attributes": {}},
            "webserver_cpu_usage": {"value": 67.0, "attributes": {}},
            "control_cpu_usage": {"value": 7.0, "attributes": {}},
            "ram_usage": {"value": 6432, "attributes": {}},
            "free_ram": {"value": 100060, "attributes": {}},
        },
        "buffer_tank": {
            "current_top_temperature": [
                {"value": 45.67, "attributes": {"upper_limit": "90", "lower_limit": "5"}},
                {"value": 35.67, "attributes": {"upper_limit": "90", "lower_limit": "5"}},
            ],
            "current_bottom_temperature": [
                {"value": 15.67, "attributes": {"upper_limit": "90", "lower_limit": "5"}},
                {"value": 25.67, "attributes": {"upper_limit": "90", "lower_limit": "5"}},
            ],
            "operating_mode": [
                {"value": "off", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
                {"value": "on", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
            ],
            "standby_temperature": [
                {"value": 10.0, "attributes": {"upper_limit": "90", "lower_limit": "0"}},
                {"value": 11.0, "attributes": {"upper_limit": "90", "lower_limit": "0"}},
            ],
            "target_temperature": [
                {"value": 42.0, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 43.0, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "heat_request": [{"value": "off", "attributes": {}}, {"value": "on", "attributes": {}}],
            "cool_request": [{"value": "on", "attributes": {}}, {"value": "off", "attributes": {}}],
        },
        "hot_water_tank": {
            "heat_request": [{"value": "off", "attributes": {}}, {"value": "on", "attributes": {}}],
            "hot_water_flow": [{"value": "off", "attributes": {}}, {"value": "on", "attributes": {}}],
            "fresh_water_module_temperature": [
                {"value": 51.23, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 51.23, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "target_temperature": [
                {"value": 51.0, "attributes": {"upper_limit": "52", "lower_limit": "0"}},
                {"value": 51.0, "attributes": {"upper_limit": "52", "lower_limit": "0"}},
            ],
            "standby_temperature": [
                {"value": 32.5, "attributes": {"upper_limit": "52", "lower_limit": "0"}},
                {"value": 32.5, "attributes": {"upper_limit": "52", "lower_limit": "0"}},
            ],
            "operating_mode": [
                {"value": "heat_up", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
                {"value": "off", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
            ],
            "current_temperature": [
                {"value": 47.7, "attributes": {"upper_limit": "90", "lower_limit": "20"}},
                {"value": 47.7, "attributes": {"upper_limit": "90", "lower_limit": "20"}},
            ],
            "circulation_return_temperature": [
                {"value": 30.45, "attributes": {"upper_limit": "100", "lower_limit": "-100"}},
                {"value": 27.45, "attributes": {"upper_limit": "100", "lower_limit": "-100"}},
            ],
            "circulation_pump_state": [{"value": "on", "attributes": {}}, {"value": "off", "attributes": {}}],
        },
        "heat_pump": {
            "circulation_pump": [{"value": 0.0, "attributes": {"upper_limit": "1", "lower_limit": "0.0"}}],
            "source_pump_speed": [{"value": 0.45, "attributes": {"upper_limit": "1", "lower_limit": "0.0"}}],
            "compressor": [{"value": 0.0, "attributes": {"upper_limit": "1", "lower_limit": "0.0"}}],
            "compressor_night_speed": [{"value": 0.5, "attributes": {"upper_limit": "1", "lower_limit": "0.5"}}],
            "compressor_input_temperature": [{"value": 27.2, "attributes": {}}],
            "compressor_output_temperature": [{"value": 27.2, "attributes": {}}],
            "compressor_use_night_speed": [{"value": "on", "attributes": {}}],
            "condenser_temperature": [{"value": 31.51, "attributes": {"upper_limit": "200", "lower_limit": "0"}}],
            "vaporizer_temperature": [{"value": -4.56, "attributes": {}}],
            "target_overheating": [{"value": 5.5, "attributes": {}}],
            "current_overheating": [{"value": 18.68, "attributes": {}}],
            "expansion_valve_position": [{"value": 20, "attributes": {}}],
            "heat_request": [{"value": "off", "attributes": {}}],
            "high_pressure": [{"value": 15.62, "attributes": {}}],
            "flow_temperature": [{"value": 24.8, "attributes": {}}],
            "low_pressure": [{"value": 15.35, "attributes": {}}],
            "name": [{"value": "WPS26", "attributes": {}}],
            "return_flow_temperature": [{"value": 23.9, "attributes": {}}],
            "source_input_temperature": [{"value": 25.7, "attributes": {}}],
            "source_output_temperature": [{"value": 24.9, "attributes": {}}],
            "state": [{"value": "standby", "attributes": {"upper_limit": "32767", "lower_limit": "0"}}],
            "substate": [{"value": "oil_preheating", "attributes": {"upper_limit": "32767", "lower_limit": "0"}}],
            "compressor_power": [{"value": 5.52, "attributes": {}}],
            "heating_power": [{"value": 3.22, "attributes": {}}],
            "hot_water_power": [{"value": 2.77, "attributes": {}}],
            "cop": [{"value": 2.55, "attributes": {}}],
            "heating_energy": [{"value": 8.43, "attributes": {}}],
            "heating_energy_consumption": [{"value": 7.33, "attributes": {}}],
            "heating_spf": [{"value": 3.32, "attributes": {}}],
            "cooling_energy": [{"value": 7.21, "attributes": {}}],
            "cooling_energy_consumption": [{"value": 8.72, "attributes": {}}],
            "cooling_spf": [{"value": 4.22, "attributes": {}}],
            "hot_water_energy": [{"value": 7.86, "attributes": {}}],
            "hot_water_energy_consumption": [{"value": 2.77, "attributes": {}}],
            "hot_water_spf": [{"value": 2.5, "attributes": {}}],
            "total_thermal_energy": [{"value": 8.22, "attributes": {}}],
            "total_energy_consumption": [{"value": 5.21, "attributes": {}}],
            "total_spf": [{"value": 2.43, "attributes": {}}],
            "operating_time": [{"value": 3809028, "attributes": {}}],
            "max_runtime": [{"value": 602403, "attributes": {}}],
            "activation_counter": [{"value": 477, "attributes": {}}],
            "has_compressor_failure": [{"value": "off", "attributes": {}}],
            "has_source_failure": [{"value": "off", "attributes": {}}],
            "has_source_actuator_failure": [{"value": "off", "attributes": {}}],
            "has_three_phase_failure": [{"value": "off", "attributes": {}}],
            "has_source_pressure_failure": [{"value": "off", "attributes": {}}],
            "has_vfd_failure": [{"value": "off", "attributes": {}}],
        },
        "heat_circuit": {
            "room_temperature": [
                {"value": 22.42, "attributes": {"upper_limit": "80", "lower_limit": "0"}},
                {"value": 22.42, "attributes": {"upper_limit": "80", "lower_limit": "0"}},
            ],
            "room_humidity": [
                {"value": 53.0, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 53.0, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "dew_point": [
                {"value": 13.1, "attributes": {"upper_limit": "50.0", "lower_limit": "-20.0"}},
                {"value": 13.1, "attributes": {"upper_limit": "50.0", "lower_limit": "-20.0"}},
            ],
            "flow_temperature_setpoint": [
                {"value": 26.55, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 26.55, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "flow_temperature": [
                {"value": 24.34, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 24.34, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "return_flow_temperature": [
                {"value": 22.21, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
                {"value": 22.21, "attributes": {"upper_limit": "100", "lower_limit": "0"}},
            ],
            "target_temperature_day": [
                {"value": 20.5, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
                {"value": 20.5, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
            ],
            "heating_limit_day": [
                {"value": 20.0, "attributes": {"upper_limit": "100", "lower_limit": "-20"}},
                {"value": 20.0, "attributes": {"upper_limit": "100", "lower_limit": "-20"}},
            ],
            "heat_request": [
                {"value": "on", "attributes": {"upper_limit": "6", "lower_limit": "0"}},
                {"value": "off", "attributes": {"upper_limit": "6", "lower_limit": "0"}},
            ],
            "cool_request": [
                {"value": "off", "attributes": {"upper_limit": "6", "lower_limit": "0"}},
                {"value": "on", "attributes": {"upper_limit": "6", "lower_limit": "0"}},
            ],
            "target_temperature_away": [
                {"value": 18.0, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
                {"value": 18.0, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
            ],
            "target_temperature_night": [
                {"value": 20.0, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
                {"value": 20.0, "attributes": {"upper_limit": "30", "lower_limit": "10"}},
            ],
            "heating_limit_night": [
                {"value": 18.0, "attributes": {"upper_limit": "100", "lower_limit": "-20"}},
                {"value": 18.0, "attributes": {"upper_limit": "100", "lower_limit": "-20"}},
            ],
            "operating_mode": [
                {"value": "day", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
                {"value": "off", "attributes": {"upper_limit": "32767", "lower_limit": "0"}},
            ],
            "selected_target_temperature": [{"value": 20.0, "attributes": {}}, {"value": 20.0, "attributes": {}}],
            "target_temperature": [
                {"value": 20.5, "attributes": {"upper_limit": "90", "lower_limit": "10"}},
                {"value": 20.5, "attributes": {"upper_limit": "90", "lower_limit": "10"}},
            ],
            "target_temperature_offset": [
                {"value": 1.5, "attributes": {"upper_limit": "2.5", "lower_limit": "-2.5"}},
                {"value": 0.0, "attributes": {"upper_limit": "2.5", "lower_limit": "-2.5"}},
            ],
            "away_start_date": [
                {"value": 1769036400, "attributes": {"upper_limit": "86400", "lower_limit": "0"}},
                {"value": 1769036400, "attributes": {"upper_limit": "86400", "lower_limit": "0"}},
            ],
            "away_end_date": [
                {"value": 1769122799, "attributes": {"upper_limit": "86400", "lower_limit": "0"}},
                {"value": 1769122799, "attributes": {"upper_limit": "86400", "lower_limit": "0"}},
            ],
            "heating_curve_offset": [
                {"value": 1.5, "attributes": {"upper_limit": "10", "lower_limit": "-10"}},
                {"value": -1.5, "attributes": {"upper_limit": "10", "lower_limit": "-10"}},
            ],
            "heating_curve_slope": [
                {"value": 0.5, "attributes": {"upper_limit": "5", "lower_limit": "0"}},
                {"value": 0.6, "attributes": {"upper_limit": "5", "lower_limit": "0"}},
            ],
            "use_heating_curve": [{"value": "off", "attributes": {}}, {"value": "on", "attributes": {}}],
            "heating_curve": [
                {
                    "value": "HC6",
                    "attributes": {
                        "points": [
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                        ],
                    },
                },
                {
                    "value": "HC7",
                    "attributes": {
                        "points": [
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                            {"outdoor": -15.0, "flow": 20.0},
                        ],
                    },
                },
            ],
            "pump_speed": [
                {"value": 0.5, "attributes": {"upper_limit": "1", "lower_limit": "0"}},
                {"value": 0.5, "attributes": {"upper_limit": "1", "lower_limit": "0"}},
            ],
        },
        "solar_circuit": {},
        "external_heat_source": {
            "operating_mode": [
                {"value": "off", "attributes": {"upper_limit": "2", "lower_limit": "0"}},
                {"value": "on", "attributes": {"upper_limit": "2", "lower_limit": "0"}},
            ],
            "target_temperature": [
                {"value": 17.23, "attributes": {"upper_limit": "90", "lower_limit": "20"}},
                {"value": 17.23, "attributes": {"upper_limit": "90", "lower_limit": "20"}},
            ],
            "heat_request": [{"value": "on", "attributes": {}}, {"value": "on", "attributes": {}}],
            "operating_time": [{"value": 812999, "attributes": {}}, {"value": 812999, "attributes": {}}],
            "max_runtime": [{"value": 8129, "attributes": {}}, {"value": 8129, "attributes": {}}],
            "activation_counter": [{"value": 812, "attributes": {}}, {"value": 812, "attributes": {}}],
        },
        "switch_valve": {
            "position": [
                {"value": "neutral", "attributes": {"upper_limit": "2", "lower_limit": "0"}},
                {"value": "open", "attributes": {"upper_limit": "2", "lower_limit": "0"}},
            ],
        },
        "photovoltaic": {},
    }
