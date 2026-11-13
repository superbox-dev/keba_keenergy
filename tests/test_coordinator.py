# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the data update coordinator."""

from __future__ import annotations

from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from homeassistant.components.switch.const import DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.const import STATE_UNKNOWN

from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import ISSUE_TRACKER_URL
from custom_components.keba_keenergy.const import REMOTE_ACCESS_SCAN_INTERVAL
from tests import get_flows_in_progress
from tests import get_state
from tests import next_update
from tests import remove_values
from tests import replace_values
from tests.const import NOW
from tests.test_coordinator_data import COMPRESSOR_POLYNOMIAL_HEAT_METER_TYPE
from tests.test_coordinator_data import ESTIMATED_FLOW_HEAT_METER_TYPE
from tests.test_coordinator_data import HEAT_CIRCUIT_ENTITY_ID
from tests.test_coordinator_data import HEAT_CIRCUIT_VALUE
from tests.test_coordinator_data import HEAT_METER_ENTITY_ID
from tests.test_coordinator_data import HEAT_PUMP_STATE_ENTITY_ID
from tests.test_coordinator_data import NO_HEAT_METER_TYPE
from tests.test_coordinator_data import OUTDOOR_TEMPERATURE_ENTITY_ID
from tests.test_coordinator_data import REMOTE_MAINTENANCE_SERVER_ENTITY_ID
from tests.test_coordinator_data import SOLAR_CIRCUIT_SECTIONS
from tests.test_coordinator_data import UNKNOWN_HEAT_METER_TYPE
from tests.test_coordinator_data import UNKNOWN_HEAT_PUMP_STATE
from tests.test_coordinator_data import WITHOUT_SOLAR_AND_HEATING_CIRCUITS_VALUES
from tests.test_coordinator_data import WITHOUT_SOLAR_CIRCUITS_DEVICE_NUMBERS_VALUES
from tests.test_coordinator_data import WITHOUT_SOLAR_CIRCUITS_VALUES
from tests.test_switch_data import MODBUS_ENTITY_ID
from tests.test_switch_data import REMOTE_ACCESS_UPDATE_REQUESTS
from tests.test_switch_data import REMOTE_MAINTENANCE_ENTITY_ID

if TYPE_CHECKING:
    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers import entity_registry as er
    from pytest_homeassistant.common import MockConfigEntry

    from tests.conftest import FakeKebaKeEnergyAPI
    from tests.const import Response

pytestmark = pytest.mark.freeze_time(NOW)


@pytest.mark.no_fail_on_keba_errors
async def test_update_authentication_error(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that rejected credentials during an update start the reauthentication flow."""
    fake_api.responses = [HTTPStatus.UNAUTHORIZED]

    await next_update(hass, freezer)

    assert get_state(hass, OUTDOOR_TEMPERATURE_ENTITY_ID).state == STATE_UNAVAILABLE
    assert get_flows_in_progress(hass) == [("reauth_confirm", DOMAIN, SOURCE_REAUTH, init_integration.entry_id)]


@pytest.mark.parametrize("error", [HTTPStatus.BAD_REQUEST, TimeoutError()], ids=["http_error", "timeout"])
@pytest.mark.no_fail_on_keba_errors
@pytest.mark.usefixtures("init_integration")
async def test_update_api_error(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
    caplog: pytest.LogCaptureFixture,
    error: Exception | HTTPStatus,
) -> None:
    """Test that the entities are unavailable if an update fails or times out, and available after the next one."""
    fake_api.responses = [error]

    await next_update(hass, freezer)

    assert get_state(hass, OUTDOOR_TEMPERATURE_ENTITY_ID).state == STATE_UNAVAILABLE
    assert "Error fetching keba_keenergy data" in caplog.text

    fake_api.responses = [fake_api.data]

    await next_update(hass, freezer)

    assert get_state(hass, OUTDOOR_TEMPERATURE_ENTITY_ID).state != STATE_UNAVAILABLE
    assert "Fetching keba_keenergy data recovered" in caplog.text


@pytest.mark.no_fail_on_keba_errors
async def test_update_curves_error(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that the update fails if the curves cannot be read after the values, and recovers with the curves."""
    fake_api.load_device("multiple_devices")
    fake_api.responses = fake_api.setup_responses(fake_api.data, fake_api.data, fake_api.data)
    await fake_api.setup_integration()

    fake_api.curve_error = HTTPStatus.BAD_REQUEST

    await next_update(hass, freezer)

    assert get_state(hass, OUTDOOR_TEMPERATURE_ENTITY_ID).state == STATE_UNAVAILABLE
    assert "Error fetching keba_keenergy data" in caplog.text

    fake_api.curve_error = None

    await next_update(hass, freezer)

    assert get_state(hass, OUTDOOR_TEMPERATURE_ENTITY_ID).state != STATE_UNAVAILABLE
    assert "Fetching keba_keenergy data recovered" in caplog.text


@pytest.mark.parametrize(
    "entry_options",
    [{"scan_interval_tick_heat_circuit": 2}],
    ids=["heat_circuit_every_second_tick"],
)
async def test_update_interval_ticks(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a device with an update multiplier of 2 is only requested every second update.

    A skipped endpoint keeps its values, the other endpoints are updated.
    """
    fake_api.load_device("multiple_devices")
    without_solar_circuits: Response = replace_values(
        remove_values(fake_api.data, *SOLAR_CIRCUIT_SECTIONS),
        WITHOUT_SOLAR_CIRCUITS_VALUES,
    )
    fake_api.device_numbers = replace_values(fake_api.device_numbers, WITHOUT_SOLAR_CIRCUITS_DEVICE_NUMBERS_VALUES)
    fake_api.responses = fake_api.setup_responses(
        without_solar_circuits,
        without_solar_circuits,
        # The values of the heating circuits are skipped on this refresh.
        replace_values(
            remove_values(fake_api.data, *SOLAR_CIRCUIT_SECTIONS, ".heatCircuit["),
            WITHOUT_SOLAR_AND_HEATING_CIRCUITS_VALUES,
        ),
    )
    await fake_api.setup_integration()

    heat_circuit_state: str = get_state(hass, HEAT_CIRCUIT_ENTITY_ID).state

    assert HEAT_CIRCUIT_VALUE in fake_api.read_requests()[-1]

    await next_update(hass, freezer)

    assert HEAT_CIRCUIT_VALUE in fake_api.read_requests()[-1]

    await next_update(hass, freezer)

    assert HEAT_CIRCUIT_VALUE not in fake_api.read_requests()[-1]
    assert get_state(hass, HEAT_CIRCUIT_ENTITY_ID).state == heat_circuit_state
    assert get_state(hass, "sensor.keba_keenergy_12345678_buffer_tank_target_temperature_1").state == "42.0"
    # The control unit has no solar circuit, so its values are never requested.
    assert not any("solarCircuit" in body for body in fake_api.read_requests())


@pytest.mark.parametrize(
    "entry_options",
    [{"scan_interval_tick_heat_circuit": 2}],
    ids=["heat_circuit_every_second_tick"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_update_interval_ticks_keep_message_ids(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a skipped device type keeps its message ids until it is requested again."""
    fake_api.load_device("multiple_devices")
    entity_id: str = "sensor.keba_keenergy_12345678_heat_circuit_room_temperature_1"
    fake_api.message_ids = {"APPL.CtrlAppl.sParam.heatCircuit[0].tempRoom.state.msgId": 50}
    without_solar_circuits: Response = replace_values(
        remove_values(fake_api.data, *SOLAR_CIRCUIT_SECTIONS),
        WITHOUT_SOLAR_CIRCUITS_VALUES,
    )
    fake_api.device_numbers = replace_values(fake_api.device_numbers, WITHOUT_SOLAR_CIRCUITS_DEVICE_NUMBERS_VALUES)
    fake_api.responses = fake_api.setup_responses(
        without_solar_circuits,
        without_solar_circuits,
        # The values of the heating circuits are skipped on this refresh.
        replace_values(
            remove_values(fake_api.data, *SOLAR_CIRCUIT_SECTIONS, ".heatCircuit["),
            WITHOUT_SOLAR_AND_HEATING_CIRCUITS_VALUES,
        ),
        without_solar_circuits,
    )
    await fake_api.setup_integration()

    # The heating circuits are requested on the first and the third refresh.
    await next_update(hass, freezer)

    assert get_state(hass, entity_id).state == STATE_UNKNOWN

    fake_api.message_ids = {}
    await next_update(hass, freezer)

    assert get_state(hass, entity_id).state == STATE_UNKNOWN

    await next_update(hass, freezer)

    assert get_state(hass, entity_id).state == "22.418831"


async def test_remote_access_not_read_while_disabled(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that the remote access is not read while all of its entities are disabled."""
    fake_api.load_device("multiple_devices")
    fake_api.responses = fake_api.setup_responses(fake_api.data, fake_api.data)
    await fake_api.setup_integration()

    await next_update(hass, freezer, interval=timedelta(seconds=REMOTE_ACCESS_SCAN_INTERVAL))

    assert fake_api.remote_access_requests() == []


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_remote_access_read_every_minute(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that the values of the enabled remote access entities are read after the setup and every minute."""
    fake_api.load_device("multiple_devices")
    fake_api.responses = fake_api.setup_responses(
        fake_api.data,
        fake_api.data,
        fake_api.data,
        fake_api.data,
    )
    await fake_api.setup_integration()

    # The other values are updated every 20 seconds.
    for _ in range(3):
        await next_update(hass, freezer)

    assert fake_api.remote_access_requests() == [
        *REMOTE_ACCESS_UPDATE_REQUESTS,
        *REMOTE_ACCESS_UPDATE_REQUESTS,
    ]


async def test_remote_access_read_only_enabled_values(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that only the values of the enabled remote access entities are read."""
    fake_api.load_device("multiple_devices")
    mock_config_entry.add_to_hass(hass)
    entity_registry.async_get_or_create(
        SWITCH_DOMAIN,
        DOMAIN,
        "12345678_modbus_active",
        config_entry=mock_config_entry,
    )
    await fake_api.setup_integration()

    assert fake_api.remote_access_requests() == ["isModbusActive"]
    assert get_state(hass, MODBUS_ENTITY_ID).state == "on"


@pytest.mark.no_fail_on_keba_errors
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "init_integration")
async def test_remote_access_update_failed(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that only the remote access entities are unavailable if reading the remote access fails.

    They are available again after the next update of the remote access.
    """
    fake_api.remote_access["isRemoteMServerReachable"] = HTTPStatus.BAD_REQUEST
    # The values are updated as well.
    fake_api.responses = [fake_api.data]

    await next_update(hass, freezer, interval=timedelta(seconds=REMOTE_ACCESS_SCAN_INTERVAL))

    assert get_state(hass, REMOTE_MAINTENANCE_SERVER_ENTITY_ID).state == STATE_UNAVAILABLE
    assert get_state(hass, REMOTE_MAINTENANCE_ENTITY_ID).state == STATE_UNAVAILABLE
    assert get_state(hass, OUTDOOR_TEMPERATURE_ENTITY_ID).state != STATE_UNAVAILABLE
    assert "Error fetching keba_keenergy_remote_access data" in caplog.text

    fake_api.remote_access["isRemoteMServerReachable"] = True
    fake_api.responses = [fake_api.data]

    await next_update(hass, freezer, interval=timedelta(seconds=REMOTE_ACCESS_SCAN_INTERVAL))

    assert get_state(hass, REMOTE_MAINTENANCE_SERVER_ENTITY_ID).state != STATE_UNAVAILABLE
    assert get_state(hass, REMOTE_MAINTENANCE_ENTITY_ID).state != STATE_UNAVAILABLE
    assert "Fetching keba_keenergy_remote_access data recovered" in caplog.text


async def test_update_unknown_value(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    freezer: FrozenDateTimeFactory,
    entity_registry: er.EntityRegistry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that values the API doesn't know are unknown and logged once with the link to report them."""
    fake_api.load_device("multiple_devices")
    fake_api.fixed_data = replace_values(fake_api.fixed_data, UNKNOWN_HEAT_METER_TYPE)
    data: Response = replace_values(fake_api.data, UNKNOWN_HEAT_PUMP_STATE)
    fake_api.responses = fake_api.setup_responses(data, data)
    await fake_api.setup_integration()

    await next_update(hass, freezer)

    assert not fake_api.responses
    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert get_state(hass, HEAT_PUMP_STATE_ENTITY_ID).state == STATE_UNKNOWN
    # An unknown heat meter type is no heat meter.
    assert entity_registry.async_get(HEAT_METER_ENTITY_ID) is None
    assert (
        caplog.text.count(f"Unknown value 9 of HeatPump.HEAT_METER_TYPE, please report it at {ISSUE_TRACKER_URL}") == 1
    )
    assert caplog.text.count(f"Unknown value 99 of HeatPump.STATE, please report it at {ISSUE_TRACKER_URL}") == 1


@pytest.mark.parametrize(
    "heat_meter_type",
    [ESTIMATED_FLOW_HEAT_METER_TYPE, COMPRESSOR_POLYNOMIAL_HEAT_METER_TYPE],
    ids=["estimated_flow", "compressor_polynomial"],
)
async def test_setup_calculated_heat_meter(
    fake_api: FakeKebaKeEnergyAPI,
    entity_registry: er.EntityRegistry,
    caplog: pytest.LogCaptureFixture,
    heat_meter_type: dict[str, str],
) -> None:
    """Test that a heat calculated by the control unit without a heat meter has the heat meter entities."""
    fake_api.load_device("multiple_devices")
    fake_api.fixed_data = replace_values(fake_api.fixed_data, heat_meter_type)
    await fake_api.setup_integration()

    assert entity_registry.async_get(HEAT_METER_ENTITY_ID) is not None
    assert "Unknown value" not in caplog.text


async def test_setup_no_heat_meter(
    fake_api: FakeKebaKeEnergyAPI,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test that a heat pump without a heat meter has no heat meter entities."""
    fake_api.load_device("multiple_devices")
    fake_api.fixed_data = replace_values(fake_api.fixed_data, NO_HEAT_METER_TYPE)
    await fake_api.setup_integration()

    assert entity_registry.async_get(HEAT_METER_ENTITY_ID) is None
