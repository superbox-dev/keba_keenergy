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
from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
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
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests("10.0.0.100")

    assert await setup.async_setup_component(hass, DOMAIN, {})

    result_1: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result_1["type"] is FlowResultType.FORM
    assert result_1["step_id"] == "user"

    result_2: ConfigFlowResult = await hass.config_entries.flow.async_configure(
        result_1["flow_id"],
        user_input={
            CONF_HOST: "10.0.0.100",
            CONF_SSL: DEFAULT_SSL,
        },
    )

    assert result_2["type"] == FlowResultType.CREATE_ENTRY
    assert result_2["result"].title == "KEBA KeEnergy (10.0.0.100)"

    assert hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "12345678")


@pytest.mark.parametrize(
    ("side_effect", "expected_error"),
    [
        (APIError("mocked api error"), "cannot_connect"),
        (ClientError("mocked client error"), "cannot_connect"),
        (Exception("mocked client error"), "unknown"),
    ],
)
async def test_user_flow_cannot_connect(hass: HomeAssistant, side_effect: Exception, expected_error: str) -> None:
    """Test when zeroconf gets an exception from the API."""
    result_1: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    with patch.object(SystemEndpoints, "get_device_info", side_effect=side_effect):
        result_2: ConfigFlowResult = await hass.config_entries.flow.async_configure(
            result_1["flow_id"],
            user_input={
                CONF_HOST: "10.0.0.100",
                CONF_SSL: DEFAULT_SSL,
            },
        )

    assert result_2["type"] == FlowResultType.FORM
    assert result_2["errors"] == {"base": expected_error}


async def test_zeroconf_flow(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the zeroconf happy flow from start to finish."""
    fake_api.responses = [MULTIPLE_POSITIONS_RESPONSE, MULTIPLE_POSITIONS_DATA_RESPONSE]
    fake_api.register_requests("ap4400.local")

    result_1: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )
    assert result_1["step_id"] == "discovery_confirm"
    assert result_1["type"] == FlowResultType.FORM
    assert result_1["description_placeholders"] == {"name": "KEBA KeEnergy", "host": "ap4400.local"}
    assert not result_1["errors"]

    progress: list[ConfigFlowResult] = hass.config_entries.flow.async_progress()
    assert len(progress) == 1
    assert progress[0].get("flow_id") == result_1["flow_id"]

    result_2: ConfigFlowResult = await hass.config_entries.flow.async_configure(result_1["flow_id"], user_input={})

    assert result_2["type"] == FlowResultType.CREATE_ENTRY
    assert result_2["result"].title == "KEBA KeEnergy (ap4400.local)"

    assert hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "12345678")


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
    "side_effect",
    [
        APIError("mocked api error"),
        ClientError("mocked client error"),
    ],
)
async def test_zeroconf_cannot_connect(hass: HomeAssistant, side_effect: Exception) -> None:
    """Test when zeroconf gets an exception from the API."""
    result_1: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZERO_CONF_SERVICE_INFO,
    )

    with patch.object(SystemEndpoints, "get_device_info", side_effect=side_effect):
        result_2: ConfigFlowResult = await hass.config_entries.flow.async_configure(result_1["flow_id"], user_input={})

    assert result_2["type"] == FlowResultType.ABORT
    assert result_2["reason"] == "cannot_connect"
