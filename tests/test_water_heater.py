import pytest
from homeassistant.components.water_heater import ATTR_OPERATION_MODE
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.components.water_heater import SERVICE_SET_OPERATION_MODE
from homeassistant.components.water_heater import STATE_ECO
from homeassistant.components.water_heater import STATE_HEAT_PUMP
from homeassistant.components.water_heater import STATE_PERFORMANCE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant
from keba_keenergy_api.constants import HotWaterTankOperatingMode
from pytest_homeassistant_custom_component.common import MockConfigEntry
from yarl import URL

from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    ("operation_mode", "expected_operating_mode"),
    [
        (STATE_ECO, HotWaterTankOperatingMode.AUTO.value),
        (STATE_PERFORMANCE, HotWaterTankOperatingMode.HEAT_UP.value),
        (STATE_OFF, HotWaterTankOperatingMode.OFF.value),
        (STATE_HEAT_PUMP, HotWaterTankOperatingMode.ON.value),
    ],
)
async def test_set_operation_mode(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    operation_mode: str,
    expected_operating_mode: str,
) -> None:
    """Test set operation mode."""
    fake_api.register_requests("10.0.0.100")
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_SET_OPERATION_MODE,
        {
            ATTR_ENTITY_ID: "water_heater.keba_keenergy_12345678_1",
            ATTR_OPERATION_MODE: operation_mode,
        },
        blocking=True,
    )

    assert (
        "POST",
        URL("http://10.0.0.100/var/readWriteVars?action=set"),
        f'[{{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "{expected_operating_mode}"}}]',
        None,
    ) in fake_api.aioclient_mock.mock_calls
