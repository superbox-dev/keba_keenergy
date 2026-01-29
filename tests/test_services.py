import pytest
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.keba_keenergy.const import ATTR_CONFIG_ENTRY
from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import SERVICE_SET_AWAY_DATE_RANGE
from custom_components.keba_keenergy.services import ATTR_END_DATE
from custom_components.keba_keenergy.services import ATTR_START_DATE
from tests import setup_integration
from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI


async def test_set_away_range(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        domain=DOMAIN,
        service=SERVICE_SET_AWAY_DATE_RANGE,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_START_DATE: "2025-01-01",
            ATTR_END_DATE: "2025-01-14",
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.start", "value": "1735686000"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.start", "value": "1735686000"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.stop", "value": "1736809200"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.stop", "value": "1736809200"}]',
    )


async def test_set_away_range_with_invalid_config_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    with pytest.raises(ServiceValidationError) as error:
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_AWAY_DATE_RANGE,
            service_data={
                ATTR_CONFIG_ENTRY: "invalid",
                ATTR_START_DATE: "2025-01-01",
                ATTR_END_DATE: "2025-01-14",
            },
            blocking=True,
        )

    assert error.value.translation_key == "invalid_config_entry"


async def test_set_away_range_with_unloaded_config_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITIONS_DATA_RESPONSE_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    # Unload the config entry
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError) as error:
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_AWAY_DATE_RANGE,
            service_data={
                ATTR_CONFIG_ENTRY: config_entry.entry_id,
                ATTR_START_DATE: "2025-01-01",
                ATTR_END_DATE: "2025-01-14",
            },
            blocking=True,
        )

    assert error.value.translation_key == "unloaded_config_entry"
