# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the config flow."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import Any

import pytest
from aiohttp import ClientError
from homeassistant.config_entries import SOURCE_USER
from homeassistant.config_entries import SOURCE_ZEROCONF
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_SSL
from homeassistant.data_entry_flow import FlowResultType

from custom_components.keba_keenergy.const import DOMAIN
from tests import get_multiple_devices_responses
from tests import replace_values
from tests.const import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.const import MULTIPLE_DEVICES_FIXED_DATA_RESPONSE
from tests.const import NOW
from tests.test_config_flow_data import CREDENTIALS
from tests.test_config_flow_data import HOST
from tests.test_config_flow_data import OPTION_KEYS
from tests.test_config_flow_data import RECONFIGURED_HOST
from tests.test_config_flow_data import UPDATE_MULTIPLIER_KEYS
from tests.test_config_flow_data import ZERO_CONF_IPV6_SERVICE_INFO
from tests.test_config_flow_data import ZERO_CONF_SERVICE_INFO
from tests.test_config_flow_data import ZEROCONF_HOST

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from homeassistant.config_entries import ConfigFlowResult
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant.common import MockConfigEntry

    from tests.conftest import FakeKebaKeEnergyAPI

pytestmark = pytest.mark.freeze_time(NOW)


async def test_user_flow(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the user flow without authentication."""
    fake_api.register_auth_request(HOST)
    fake_api.register_get_device_info(HOST)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result.get("errors")

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: HOST, CONF_SSL: False},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].title == "KEBA KeEnergy (10.0.0.100)"
    assert result["data"] == {CONF_HOST: HOST, CONF_SSL: False}
    assert result["result"].unique_id == "12345678"
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.usefixtures("mock_setup_entry")
async def test_user_flow_already_configured(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the user flow aborts for a device that is already configured."""
    mock_config_entry.add_to_hass(hass)
    fake_api.register_auth_request(HOST)
    fake_api.register_get_device_info(HOST)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: HOST},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_authentication(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the user flow with authentication."""
    fake_api.register_auth_request(HOST, status=HTTPStatus.UNAUTHORIZED)
    fake_api.register_get_device_info(HOST, ssl=True)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result.get("errors")

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: HOST, CONF_SSL: True},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=CREDENTIALS)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].title == "KEBA KeEnergy (10.0.0.100)"
    assert result["result"].data == {**CREDENTIALS, CONF_HOST: HOST, CONF_SSL: True}
    assert result["result"].unique_id == "12345678"
    assert len(mock_setup_entry.mock_calls) == 1


async def test_user_flow_authentication_invalid_auth(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the authentication step of the user flow shows an error for invalid credentials."""
    fake_api.register_auth_request(HOST, status=HTTPStatus.UNAUTHORIZED)
    fake_api.register_get_device_info(HOST, ssl=True, status=HTTPStatus.UNAUTHORIZED)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: HOST, CONF_SSL: True},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={**CREDENTIALS, CONF_PASSWORD: "wrong"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_authentication_check_failed(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the user flow creates the entry without credentials if the check for them fails."""
    fake_api.register_auth_request(HOST, exc=ClientError())
    fake_api.register_get_device_info(HOST, ssl=True)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result.get("errors")

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: HOST, CONF_SSL: True},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].title == "KEBA KeEnergy (10.0.0.100)"
    assert result["result"].unique_id == "12345678"
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    ("status", "exc", "expected_error"),
    [
        (HTTPStatus.BAD_REQUEST, None, "cannot_connect"),
        (HTTPStatus.UNAUTHORIZED, None, "invalid_auth"),
        (HTTPStatus.OK, ValueError("mocked client error"), "unknown"),
    ],
    ids=["cannot_connect", "invalid_auth", "unknown"],
)
@pytest.mark.no_fail_on_keba_errors
async def test_user_flow_errors(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    status: HTTPStatus,
    exc: Exception | None,
    expected_error: str,
) -> None:
    """Test the errors of the user flow."""
    fake_api.register_auth_request(HOST)
    fake_api.register_get_device_info(HOST, status=status, exc=exc)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: HOST, CONF_SSL: False},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": expected_error}


@pytest.mark.usefixtures("mock_setup_entry")
async def test_reconfigure_flow_authentication(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the reconfiguration flow with authentication."""
    fake_api.register_auth_request(RECONFIGURED_HOST, status=HTTPStatus.UNAUTHORIZED)
    fake_api.register_get_device_info(RECONFIGURED_HOST, ssl=True)
    mock_config_entry.add_to_hass(hass)

    result: ConfigFlowResult = await mock_config_entry.start_reconfigure_flow(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result.get("errors")

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: RECONFIGURED_HOST, CONF_SSL: True},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=CREDENTIALS)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"


@pytest.mark.parametrize("entry_data", [{CONF_HOST: HOST, CONF_SSL: True}], ids=["ssl"])
@pytest.mark.usefixtures("mock_setup_entry")
async def test_reauth_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the reauthentication flow with valid credentials."""
    fake_api.register_get_device_info(HOST, ssl=True)
    mock_config_entry.add_to_hass(hass)

    result: ConfigFlowResult = await mock_config_entry.start_reauth_flow(hass, data={CONF_HOST: HOST, CONF_SSL: True})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=CREDENTIALS)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data == {CONF_HOST: HOST, CONF_SSL: True, **CREDENTIALS}


@pytest.mark.parametrize(
    ("unique_id", "device_info_status", "expected"),
    [
        ("12345678", HTTPStatus.UNAUTHORIZED, {"type": FlowResultType.FORM, "errors": {"base": "invalid_auth"}}),
        ("12345679", HTTPStatus.OK, {"type": FlowResultType.ABORT, "reason": "wrong_account"}),
    ],
    ids=["invalid_auth", "wrong_account"],
)
@pytest.mark.usefixtures("mock_setup_entry")
async def test_reauth_flow_errors(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    unique_id: str,
    device_info_status: HTTPStatus,
    expected: dict[str, object],
) -> None:
    """Test that the reauthentication flow shows invalid credentials and aborts for another device."""
    fake_api.register_get_device_info(HOST, ssl=True, status=device_info_status)
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(mock_config_entry, unique_id=unique_id)

    result: ConfigFlowResult = await mock_config_entry.start_reauth_flow(hass, data={CONF_HOST: HOST, CONF_SSL: True})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=CREDENTIALS)

    assert {key: result.get(key) for key in expected} == expected


async def test_zeroconf_flow(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the zeroconf discovery flow without authentication."""
    fake_api.register_auth_request(ZEROCONF_HOST)
    fake_api.register_get_device_info(ZEROCONF_HOST)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"
    assert result["description_placeholders"] == {"name": "KEBA KeEnergy", "host": ZEROCONF_HOST}
    assert not result["errors"]

    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input={})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].title == "KEBA KeEnergy (ap4400.local)"
    assert result["result"].unique_id == "12345678"
    assert len(mock_setup_entry.mock_calls) == 1


async def test_zeroconf_flow_authentication(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the zeroconf discovery flow with authentication."""
    fake_api.register_auth_request(ZEROCONF_HOST, status=HTTPStatus.UNAUTHORIZED)
    fake_api.register_get_device_info(ZEROCONF_HOST, ssl=True)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["description_placeholders"] == {"name": "KEBA KeEnergy"}
    assert not result["errors"]

    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=CREDENTIALS)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].title == "KEBA KeEnergy (ap4400.local)"
    assert result["result"].unique_id == "12345678"
    assert len(mock_setup_entry.mock_calls) == 1


async def test_zeroconf_flow_authentication_check_failed(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the zeroconf discovery flow asks for confirmation without credentials if the check for them fails."""
    fake_api.register_auth_request(ZEROCONF_HOST, exc=ClientError())
    fake_api.register_get_device_info(ZEROCONF_HOST, ssl=True)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"


@pytest.mark.parametrize(
    ("status", "exc", "expected_error"),
    [
        (HTTPStatus.BAD_REQUEST, None, "cannot_connect"),
        (HTTPStatus.UNAUTHORIZED, None, "invalid_auth"),
        (HTTPStatus.OK, ValueError("mocked client error"), "unknown"),
    ],
    ids=["cannot_connect", "invalid_auth", "unknown"],
)
@pytest.mark.no_fail_on_keba_errors
async def test_zeroconf_flow_errors(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    status: HTTPStatus,
    exc: Exception | None,
    expected_error: str,
) -> None:
    """Test the errors of the zeroconf discovery flow."""
    fake_api.register_auth_request(ZEROCONF_HOST)
    fake_api.register_get_device_info(ZEROCONF_HOST, status=status, exc=exc)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input={})

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": expected_error}


@pytest.mark.usefixtures("mock_setup_entry")
async def test_zeroconf_flow_already_configured(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that the zeroconf discovery flow aborts for a configured device."""
    mock_config_entry.add_to_hass(hass)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    ("entry_data", "expected_host"),
    [
        ({CONF_HOST: "10.0.0.50", CONF_SSL: False}, HOST),
        ({CONF_HOST: "keba.local", CONF_SSL: False}, "keba.local"),
    ],
    ids=["ip_address_updated", "hostname_kept"],
)
@pytest.mark.usefixtures("mock_setup_entry")
async def test_zeroconf_flow_updates_ip_address(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    expected_host: str,
) -> None:
    """Test that the zeroconf discovery updates a changed IP address, but keeps a configured host name."""
    mock_config_entry.add_to_hass(hass)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert mock_config_entry.data[CONF_HOST] == expected_host


@pytest.mark.usefixtures("mock_setup_entry")
async def test_zeroconf_flow_keeps_ip_address_for_ipv6(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that the zeroconf discovery does not replace the IP address with an IPv6 address."""
    mock_config_entry.add_to_hass(hass)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_IPV6_SERVICE_INFO,
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert mock_config_entry.data[CONF_HOST] == HOST


@pytest.mark.parametrize(
    ("user_input", "expected"),
    [
        (
            {
                "scan_interval": 60,
                "update_multipliers": {
                    "scan_interval_tick_system": 4,
                    "scan_interval_tick_heat_pump": 4,
                    "scan_interval_tick_heat_circuit": 8,
                    "scan_interval_tick_solar_circuit": 2,
                    "scan_interval_tick_hot_water_tank": 2,
                    "scan_interval_tick_buffer_tank": 16,
                    "scan_interval_tick_switch_valve": 2,
                    "scan_interval_tick_external_heat_source": 4,
                    "scan_interval_tick_photovoltaics": 2,
                },
                "display": {
                    "mixer_position_percent": True,
                },
            },
            {
                "scan_interval": 120,
                "scan_interval_tick_system": 2,
                "scan_interval_tick_heat_pump": 2,
                "scan_interval_tick_heat_circuit": 4,
                "scan_interval_tick_solar_circuit": 1,
                "scan_interval_tick_hot_water_tank": 1,
                "scan_interval_tick_buffer_tank": 8,
                "scan_interval_tick_switch_valve": 1,
                "scan_interval_tick_external_heat_source": 2,
                "scan_interval_tick_photovoltaics": 1,
                "mixer_position_percent": True,
            },
        ),
        (
            {
                "scan_interval": 60,
                "update_multipliers": {
                    "scan_interval_tick_system": 1,
                    "scan_interval_tick_heat_pump": 2,
                    "scan_interval_tick_heat_circuit": 3,
                    "scan_interval_tick_solar_circuit": 1,
                    "scan_interval_tick_hot_water_tank": 1,
                    "scan_interval_tick_buffer_tank": 1,
                    "scan_interval_tick_switch_valve": 1,
                    "scan_interval_tick_external_heat_source": 1,
                    "scan_interval_tick_photovoltaics": 1,
                },
                "display": {
                    "mixer_position_percent": True,
                },
            },
            {
                "scan_interval": 60,
                "scan_interval_tick_system": 1,
                "scan_interval_tick_heat_pump": 2,
                "scan_interval_tick_heat_circuit": 3,
                "scan_interval_tick_solar_circuit": 1,
                "scan_interval_tick_hot_water_tank": 1,
                "scan_interval_tick_buffer_tank": 1,
                "scan_interval_tick_switch_valve": 1,
                "scan_interval_tick_external_heat_source": 1,
                "scan_interval_tick_photovoltaics": 1,
                "mixer_position_percent": True,
            },
        ),
    ],
    ids=["divided_by_common_divisor", "no_common_divisor"],
)
async def test_options_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    user_input: dict[str, Any],
    expected: dict[str, bool | int],
) -> None:
    """Test the options flow, the options without sections and the normalization of the update multipliers."""
    fake_api.responses = [
        # The first setup of the coordinator.
        *get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE),
        # The second setup of the coordinator after the reload.
        *get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE),
    ]
    await fake_api.setup_integration()

    result: ConfigFlowResult = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"
    assert result["data_schema"]
    assert list(result["data_schema"].schema.keys()) == OPTION_KEYS
    assert list(result["data_schema"].schema["update_multipliers"].schema.schema.keys()) == UPDATE_MULTIPLIER_KEYS

    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input=user_input)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == expected
    # The number selectors return floats, the options are stored as integers.
    assert {type(value) for value in result["data"].values()} == {bool, int}


async def test_options_flow_without_photovoltaics(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the options flow hides the photovoltaics multiplier without photovoltaics."""
    fake_api.responses = get_multiple_devices_responses(
        [value for value in MULTIPLE_DEVICES_DATA_RESPONSE if ".photovoltaics." not in value["name"]],
        fixed_data=replace_values(
            MULTIPLE_DEVICES_FIXED_DATA_RESPONSE,
            {"APPL.CtrlAppl.sParam.options.hasPhotovoltaics": "false"},
        ),
    )
    await fake_api.setup_integration()

    result: ConfigFlowResult = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"
    assert result["data_schema"]
    assert list(result["data_schema"].schema["update_multipliers"].schema.schema.keys()) == [
        key for key in UPDATE_MULTIPLIER_KEYS if key != "scan_interval_tick_photovoltaics"
    ]


async def test_options_flow_when_integration_unloaded(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test that the options flow aborts if the integration was unloaded."""
    await hass.config_entries.async_unload(init_integration.entry_id)

    assert init_integration.state is ConfigEntryState.NOT_LOADED

    result: ConfigFlowResult = await hass.config_entries.options.async_init(init_integration.entry_id)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "options_not_ready"


async def test_options_flow_when_integration_reload_failed(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the options flow aborts if a reload of the integration failed."""
    fake_api.responses = [
        *get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE),
        # The reload fails.
        HTTPStatus.BAD_REQUEST,
    ]
    await fake_api.setup_integration()
    await hass.config_entries.async_reload(mock_config_entry.entry_id)

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY

    result: ConfigFlowResult = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "options_not_ready"
