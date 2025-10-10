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

from custom_components.keba_keenergy.const import DEFAULT_SSL
from custom_components.keba_keenergy.const import DOMAIN
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multi_positions_data_response
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
    """Test user happy flow from start to finish."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
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
    """Test user happy flow from start to finish with authentication."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
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


async def test_user_flow_authentication_cannot_connect(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test user flow authentication with cannot connect error."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
    fake_api.register_auth_request("10.0.0.100", status=401, exc=ClientError())
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

    assert result_auth_step["type"] == FlowResultType.ABORT
    assert result_auth_step["reason"] == "cannot_connect"


@pytest.mark.parametrize(
    ("side_effect", "expected_error"),
    [
        (APIError("mocked api error"), "cannot_connect"),
        (APIError("mocked api error", status=HTTPStatus.UNAUTHORIZED), "invalid_auth"),
        (Exception("mocked client error"), "unknown"),
    ],
)
async def test_user_flow_cannot_connect(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    side_effect: Exception,
    expected_error: str,
) -> None:
    """Test when zeroconf gets an exception from the API."""
    fake_api.register_auth_request("10.0.0.100")

    result_user_step_1: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    with patch.object(SystemEndpoints, "get_device_info", side_effect=side_effect):
        result_user_step_2: ConfigFlowResult = await hass.config_entries.flow.async_configure(
            result_user_step_1["flow_id"],
            user_input={
                CONF_HOST: "10.0.0.100",
                CONF_SSL: DEFAULT_SSL,
            },
        )

    assert result_user_step_2["type"] == FlowResultType.FORM
    assert result_user_step_2["errors"] == {"base": expected_error}


async def test_zeroconf_flow(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the zeroconf happy flow from start to finish."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
    fake_api.register_auth_request("ap4400.local")
    fake_api.register_requests("ap4400.local")

    result_discovery_confirm: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )
    assert result_discovery_confirm["step_id"] == "discovery_confirm"
    assert result_discovery_confirm["type"] == FlowResultType.FORM
    assert result_discovery_confirm["description_placeholders"] == {"name": "KEBA KeEnergy", "host": "ap4400.local"}
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
    """Test the zeroconf happy flow from start to finish with authentication."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
    fake_api.register_auth_request("ap4400.local", status=401)
    fake_api.register_requests("ap4400.local", ssl=True)

    result_auth_step: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )
    assert result_auth_step["step_id"] == "auth"
    assert result_auth_step["type"] == FlowResultType.FORM
    assert result_auth_step["description_placeholders"] is None
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
    """Test the zeroconf happy flow from start to finish with authentication."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, get_multi_positions_data_response()]
    fake_api.register_auth_request("ap4400.local", status=401, exc=ClientError())
    fake_api.register_requests("ap4400.local", ssl=True)

    result_auth_step: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    assert result_auth_step["type"] == FlowResultType.ABORT
    assert result_auth_step["reason"] == "cannot_connect"


async def test_zeroconf_flow_already_setup(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Test zeroconf discovery with already setup device."""
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
async def test_zeroconf_cannot_connect(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    side_effect: Exception,
    expected_error: str,
) -> None:
    """Test when zeroconf gets an exception from the API."""
    fake_api.register_auth_request("ap4400.local")

    result_discovery_confirm_1: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    with patch.object(SystemEndpoints, "get_device_info", side_effect=side_effect):
        result_discovery_confirm_2: ConfigFlowResult = await hass.config_entries.flow.async_configure(
            result_discovery_confirm_1["flow_id"],
            user_input={},
        )

    assert result_discovery_confirm_2["type"] == FlowResultType.FORM
    assert result_discovery_confirm_2["errors"] == {"base": expected_error}
