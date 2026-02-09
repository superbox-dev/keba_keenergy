import pytest
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.keba_keenergy.const import ATTR_CONFIG_ENTRY
from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import SERVICE_SET_AWAY_DATE_RANGE
from custom_components.keba_keenergy.const import SERVICE_SET_HEATING_CURVE_POINTS
from custom_components.keba_keenergy.services import ATTR_END_DATE
from custom_components.keba_keenergy.services import ATTR_HEATING_CURVE
from custom_components.keba_keenergy.services import ATTR_POINTS
from custom_components.keba_keenergy.services import ATTR_START_DATE
from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1
from tests.api_data import HEATING_CURVES_RESPONSE_2
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
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
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
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
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.stop", "value": "1736895599"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.stop", "value": "1736895599"}]',
    )


async def test_set_away_range_with_invalid_start_and_end_date(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    with pytest.raises(
        ServiceValidationError,
        match="The end date must not be earlier than the start date",
    ):
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_AWAY_DATE_RANGE,
            service_data={
                ATTR_CONFIG_ENTRY: config_entry.entry_id,
                ATTR_START_DATE: "2025-01-14",
                ATTR_END_DATE: "2025-01-01",
            },
            blocking=True,
        )


async def test_set_away_range_with_invalid_config_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    with pytest.raises(
        ServiceValidationError,
        match=r"Invalid integration provided\. Got invalid",
    ):
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


async def test_set_away_range_with_unloaded_config_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    # Unload the config entry
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(
        ServiceValidationError,
        match=r"Invalid integration provided\. KEBA KeEnergy \(ap4400\.local\) is not loaded",
    ):
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


async def test_set_heating_curve_points(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1,
        HEATING_CURVES_RESPONSE_2,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    await hass.services.async_call(
        domain=DOMAIN,
        service=SERVICE_SET_HEATING_CURVE_POINTS,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_HEATING_CURVE: "hc1",
            ATTR_POINTS: [
                {"outdoor": -20, "flow": 35.30},
                {"outdoor": 20, "flow": 23.9},
                {"outdoor": -15, "flow": 33.9},
                {"outdoor": 15, "flow": 25.3},
                {"outdoor": -10, "flow": 32.5},
                {"outdoor": 10, "flow": 26.7},
                {"outdoor": -5, "flow": 31.1},
                {"outdoor": 5, "flow": 28.1},
                {"outdoor": 0, "flow": 29.5},
            ],
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        '[{"name": "APPL.CtrlAppl.sParam.linTabPool[0].noOfPoints", "value": "9"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[0].x", "value": "-20.0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[0].y", "value": "35.3"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[1].x", "value": "-15.0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[1].y", "value": "33.9"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[2].x", "value": "-10.0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[2].y", "value": "32.5"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[3].x", "value": "-5.0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[3].y", "value": "31.1"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[4].x", "value": "0.0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[4].y", "value": "29.5"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[5].x", "value": "5.0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[5].y", "value": "28.1"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[6].x", "value": "10.0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[6].y", "value": "26.7"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[7].x", "value": "15.0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[7].y", "value": "25.3"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[8].x", "value": "20.0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[8].y", "value": "23.9"}]',
    )
