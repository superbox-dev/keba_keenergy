from ipaddress import ip_address
from typing import TYPE_CHECKING

from homeassistant import setup
from homeassistant.config_entries import SOURCE_ZEROCONF
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from custom_components.keba_keenergy.const import DOMAIN
from tests.conftest import FakeKebaKeEnergyAPI

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult


async def test_zeroconf_flow(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the zeroconf happy flow from start to finish."""
    fake_api.register_requests()

    assert await setup.async_setup_component(hass, DOMAIN, {})

    result_1: ConfigFlowResult = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZeroconfServiceInfo(
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
        ),
    )
    assert result_1["step_id"] == "discovery_confirm"
    assert result_1["type"] == FlowResultType.FORM
    assert result_1["description_placeholders"] == {"name": "KEBA KeEnergy", "host": "ap4400.local"}
    assert not result_1["errors"]

    progress: list[ConfigFlowResult] = hass.config_entries.flow.async_progress()
    assert len(progress) == 1
    assert progress[0].get("flow_id") == result_1["flow_id"]

    result_2: ConfigFlowResult = await hass.config_entries.flow.async_configure(result_1["flow_id"], user_input={})

    assert result_2["type"] is FlowResultType.CREATE_ENTRY
    assert result_2["result"].title == "KEBA KeEnergy (ap4400.local)"

    assert hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "12345678")
