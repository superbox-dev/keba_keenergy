from http import HTTPStatus
from ipaddress import ip_address
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from aiohttp import ClientError
from homeassistant import setup
from homeassistant.config_entries import SOURCE_USER
from homeassistant.config_entries import SOURCE_ZEROCONF
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_SSL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from keba_keenergy_api.endpoints import SystemEndpoints
from keba_keenergy_api.error import APIError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.keba_keenergy.const import DOMAIN
from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import HEATING_CURVE_NAMES_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult

ZERO_CONF_SERVICE_INFO: ZeroconfServiceInfo = ZeroconfServiceInfo(
    ip_address=ip_address("10.0.0.100"),
    ip_addresses=[ip_address("10.0.0.100")],
    port=0,
    hostname="ap4400.local.",
    type="_keba-device._tcp.local.",
    name="ap4400._keba-device._tcp.local.'",
    properties={
        "devicename": "AP 440/H-A",
        "serialnumber": "12345678",
    },
)


async def test_user_flow(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_auth_request("10.0.0.100")
    fake_api.register_requests("10.0.0.100")

    assert await setup.async_setup_component(hass, DOMAIN, {})

    result_user_step: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result_user_step["type"] is FlowResultType.FORM
    assert result_user_step["step_id"] == "user"

    result_create_entry: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_user_step["flow_id"],
        user_input={
            CONF_HOST: "10.0.0.100",
            CONF_SSL: False,
        },
    )

    assert result_create_entry["type"] == FlowResultType.CREATE_ENTRY
    assert result_create_entry["result"].title == "KEBA KeEnergy (10.0.0.100)"
    assert result_create_entry["data"] == {
        "host": "10.0.0.100",
        "ssl": False,
    }

    assert hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "12345678")


async def test_user_flow_authentication(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_auth_request("10.0.0.100", status=401)
    fake_api.register_requests("10.0.0.100", ssl=True)

    assert await setup.async_setup_component(hass, DOMAIN, {})

    result_user_step: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result_user_step["type"] is FlowResultType.FORM
    assert result_user_step["step_id"] == "user"

    result_auth_step: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_user_step["flow_id"],
        user_input={
            CONF_HOST: "10.0.0.100",
            CONF_SSL: True,
        },
    )

    assert result_auth_step["type"] == FlowResultType.FORM

    result_create_entry: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_user_step["flow_id"],
        user_input={
            "username": "test",
            "password": "test",
        },
    )

    assert result_create_entry["result"].title == "KEBA KeEnergy (10.0.0.100)"
    assert result_create_entry["result"].data == {
        "username": "test",
        "password": "test",
        "host": "10.0.0.100",
        "ssl": True,
    }

    assert hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "12345678")


async def test_reconfigure_flow_authentication(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]

    fake_api.register_auth_request("10.0.0.200", status=401)
    fake_api.register_requests("10.0.0.200", ssl=True)

    config_entry.add_to_hass(hass)

    result: ConfigFlowResult = await config_entry.start_reconfigure_flow(hass)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result_user_step: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "host": "10.0.0.200",
            "ssl": True,
        },
    )

    assert result_user_step["type"] == FlowResultType.FORM
    assert result_user_step["step_id"] == "auth"

    result_auth_step: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "username": "test",
            "password": "test",
        },
    )

    assert result_auth_step["type"] == FlowResultType.ABORT
    assert result_auth_step["reason"] == "reconfigure_successful"


async def test_user_flow_authentication_cannot_connect(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_auth_request("10.0.0.100", exc=ClientError())
    fake_api.register_requests("10.0.0.100", ssl=True)

    assert await setup.async_setup_component(hass, DOMAIN, {})

    result_user_step: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result_user_step["type"] is FlowResultType.FORM
    assert result_user_step["step_id"] == "user"

    result_auth_step: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_user_step["flow_id"],
        user_input={
            "host": "10.0.0.100",
            "ssl": True,
        },
    )

    assert result_auth_step["type"] == FlowResultType.CREATE_ENTRY
    assert result_auth_step["result"].title == "KEBA KeEnergy (10.0.0.100)"

    assert hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "12345678")


@pytest.mark.parametrize(
    "config_entry",
    [
        {
            "data": {
                "ssl": True,
            },
        },
    ],
    indirect=True,
)
async def test_reauth_flow_success(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests("10.0.0.100", ssl=True)

    config_entry.add_to_hass(hass)

    result_start_reauth: ConfigFlowResult = await config_entry.start_reauth_flow(
        hass,
        data={
            "host": "10.0.0.100",
            "ssl": True,
        },
    )

    assert result_start_reauth["type"] is FlowResultType.FORM
    assert result_start_reauth["step_id"] == "reauth_confirm"
    assert result_start_reauth["errors"] == {}

    result: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_start_reauth["flow_id"],
        user_input={
            "username": "test",
            "password": "test",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"


async def test_reauth_flow_failure(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.register_get_device_info("10.0.0.100", ssl=True, status=401)

    config_entry.add_to_hass(hass)

    result_start_reauth: ConfigFlowResult = await config_entry.start_reauth_flow(
        hass,
        data={
            "host": "10.0.0.100",
            "ssl": True,
        },
    )

    assert result_start_reauth["type"] is FlowResultType.FORM
    assert result_start_reauth["step_id"] == "reauth_confirm"
    assert result_start_reauth["errors"] == {}

    result: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_start_reauth["flow_id"],
        user_input={
            "username": "test",
            "password": "test",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"] == {
        "base": "invalid_auth",
    }


@pytest.mark.parametrize(
    "config_entry",
    [
        {
            "unique_id": "12345679",
        },
    ],
    indirect=True,
)
async def test_reauth_flow_wrong_account(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.register_get_device_info("10.0.0.100", ssl=True)

    config_entry.add_to_hass(hass)

    result_start_reauth: ConfigFlowResult = await config_entry.start_reauth_flow(
        hass,
        data={
            "host": "10.0.0.100",
            "ssl": True,
        },
    )

    assert result_start_reauth["type"] is FlowResultType.FORM
    assert result_start_reauth["step_id"] == "reauth_confirm"
    assert result_start_reauth["errors"] == {}

    result: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_start_reauth["flow_id"],
        user_input={
            "username": "test",
            "password": "test",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "wrong_account"


@pytest.mark.parametrize(
    ("side_effect", "expected_error"),
    [
        (APIError("mocked api error"), "cannot_connect"),
        (APIError("mocked api error", status=HTTPStatus.UNAUTHORIZED), "invalid_auth"),
        (Exception("mocked client error"), "unknown"),
    ],
)
@pytest.mark.no_fail_on_keba_errors
async def test_user_flow_cannot_connect(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    side_effect: Exception,
    expected_error: str,
) -> None:
    fake_api.register_auth_request("10.0.0.100")

    result_user_step_1: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    with patch.object(SystemEndpoints, "get_device_info", side_effect=side_effect):
        result_user_step_2: ConfigFlowResult = await hass.config_entries.flow.async_configure(
            result_user_step_1["flow_id"],
            user_input={
                "host": "10.0.0.100",
                "ssl": False,
            },
        )

    assert result_user_step_2["type"] == FlowResultType.FORM
    assert result_user_step_2["errors"] == {"base": expected_error}


async def test_zeroconf_flow(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_auth_request("ap4400.local")
    fake_api.register_requests("ap4400.local")

    result_discovery_confirm: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )
    assert result_discovery_confirm["step_id"] == "discovery_confirm"
    assert result_discovery_confirm["type"] == FlowResultType.FORM
    assert result_discovery_confirm["description_placeholders"] == {
        "name": "KEBA KeEnergy",
        "host": "ap4400.local",
    }
    assert not result_discovery_confirm["errors"]

    result_create_entry: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_discovery_confirm["flow_id"],
        user_input={},
    )

    assert result_create_entry["type"] == FlowResultType.CREATE_ENTRY
    assert result_create_entry["result"].title == "KEBA KeEnergy (ap4400.local)"

    assert hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "12345678")


async def test_zeroconf_flow_authentication(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_auth_request("ap4400.local", status=401)
    fake_api.register_requests("ap4400.local", ssl=True)

    result_auth_step: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )
    assert result_auth_step["step_id"] == "auth"
    assert result_auth_step["type"] == FlowResultType.FORM
    assert result_auth_step["description_placeholders"] == {
        "name": "KEBA KeEnergy",
    }
    assert not result_auth_step["errors"]

    result_create_entry: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_auth_step["flow_id"],
        user_input={
            "username": "test",
            "password": "test",
        },
    )

    assert result_create_entry["type"] == FlowResultType.CREATE_ENTRY
    assert result_create_entry["result"].title == "KEBA KeEnergy (ap4400.local)"

    assert hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "12345678")


async def test_zeroconf_flow_authentication_cannot_connect(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    fake_api.register_auth_request("ap4400.local", exc=ClientError())
    fake_api.register_requests("ap4400.local", ssl=True)

    result_auth_step: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    assert result_auth_step["type"] == FlowResultType.FORM
    assert result_auth_step["step_id"] == "discovery_confirm"


async def test_zeroconf_flow_already_setup(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    config_entry.add_to_hass(hass)

    result: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    ("side_effect", "expected_error"),
    [
        (APIError("mocked api error"), "cannot_connect"),
        (APIError("mocked api error", status=HTTPStatus.UNAUTHORIZED), "invalid_auth"),
        (Exception("mocked client error"), "unknown"),
    ],
)
@pytest.mark.no_fail_on_keba_errors
async def test_zeroconf_cannot_connect(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    side_effect: Exception,
    expected_error: str,
) -> None:
    fake_api.register_auth_request("ap4400.local")
    fake_api.register_get_device_info("ap4400.local", ssl=False, exc=side_effect)

    result_discovery_confirm_1: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    result_discovery_confirm_2: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_discovery_confirm_1["flow_id"],
        user_input={},
    )

    assert result_discovery_confirm_2["type"] == FlowResultType.FORM
    assert result_discovery_confirm_2["errors"] == {"base": expected_error}


async def test_option_flow(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        # 1. coordinator
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
        # 2. coordinator
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    result_init: ConfigFlowResult = await hass.config_entries.options.async_init(
        config_entry.entry_id,
        data=None,
    )

    assert result_init["type"] is FlowResultType.FORM
    assert result_init["step_id"] == "init"
    assert result_init["data_schema"]

    assert list(result_init["data_schema"].schema.keys()) == [
        "scan_interval",
        "scan_interval_tick_system",
        "scan_interval_tick_heat_pump",
        "scan_interval_tick_heat_circuit",
        "scan_interval_tick_solar_circuit",
        "scan_interval_tick_hot_water_tank",
        "scan_interval_tick_buffer_tank",
        "scan_interval_tick_switch_valve",
        "scan_interval_tick_external_heat_source",
    ]

    result_create_entry: ConfigFlowResult = await hass.config_entries.options.async_configure(
        result_init["flow_id"],
        user_input={
            "scan_interval": 60,
            "scan_interval_tick_system": 2,
            "scan_interval_tick_heat_pump": 2,
            "scan_interval_tick_heat_circuit": 4,
            "scan_interval_tick_solar_circuit": 1,
            "scan_interval_tick_hot_water_tank": 1,
            "scan_interval_tick_buffer_tank": 8,
            "scan_interval_tick_switch_valve": 1,
            "scan_interval_tick_external_heat_source": 2,
        },
    )

    assert result_create_entry["type"] is FlowResultType.CREATE_ENTRY
    assert result_create_entry["data"] == {
        "scan_interval": 60,
        "scan_interval_tick_system": 2,
        "scan_interval_tick_heat_pump": 2,
        "scan_interval_tick_heat_circuit": 4,
        "scan_interval_tick_solar_circuit": 1,
        "scan_interval_tick_hot_water_tank": 1,
        "scan_interval_tick_buffer_tank": 8,
        "scan_interval_tick_switch_valve": 1,
        "scan_interval_tick_external_heat_source": 2,
    }


async def test_option_flow_when_integration_not_fully_loaded(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        # 1. coordinator
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)
    config_entry.runtime_data = None

    result_init: ConfigFlowResult = await hass.config_entries.options.async_init(
        config_entry.entry_id,
        data=None,
    )

    assert result_init["type"] == FlowResultType.ABORT
    assert result_init["reason"] == "options_not_ready"
