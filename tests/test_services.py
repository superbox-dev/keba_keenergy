from typing import Any

import pytest
import voluptuous as vol
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
from custom_components.keba_keenergy.services import AWAY_DATE_RANGE_SCHEMA
from custom_components.keba_keenergy.services import HEATING_CURVE_POINTS_SCHEMA
from tests import init_translations
from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import HEATING_CURVES_RESPONSE_1_2
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
        HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
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
        HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="exceptions")

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

    assert (
        translations["component.keba_keenergy.exceptions.end_date_smaller_than_start_date.message"]
        == "Das Enddatum darf nicht vor dem Startdatum liegen."
    )


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "Invalid integration provided. Got {config_entry_id}."),
        ("de", "Ungültige Integration angegeben. {config_entry_id} erhalten."),
    ],
)
async def test_set_away_range_with_invalid_config_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    language: str,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = language
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="exceptions")

    with pytest.raises(ServiceValidationError):
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

    assert translations["component.keba_keenergy.exceptions.invalid_config_entry.message"] == expected


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "Invalid integration provided. {config_entry_id} is not loaded."),
        ("de", "Ungültige Integration angegeben. {config_entry_id} ist nicht geladen."),
    ],
)
async def test_set_away_range_with_unloaded_config_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    language: str,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = language
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="exceptions")

    # Unload the config entry
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError):
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

    assert translations["component.keba_keenergy.exceptions.unloaded_config_entry.message"] == expected


async def test_set_heating_curve_points(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        HEATING_CURVES_RESPONSE_1_1,
        HEATING_CURVES_RESPONSE_2,
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
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[8].y", "value": "23.9"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[9].x", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[9].y", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[10].x", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[10].y", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[11].x", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[11].y", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[12].x", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[12].y", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[13].x", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[13].y", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[14].x", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[14].y", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[15].x", "value": "0"}, '
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[15].y", "value": "0"}, '
        '{"name": "APPL.CtrlApplsParam.linTabPool[0].verCnt", "value": "192"}]',
    )


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", 'Can not find heating curve "{heating_curve}".'),
        ("de", 'Heizkurve "{heating_curve}" nicht gefunden.'),
    ],
)
async def test_set_heating_curve_points_with_invalid_heating_curve(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    language: str,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        HEATING_CURVES_RESPONSE_1_2,
        HEATING_CURVES_RESPONSE_2,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = language
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="exceptions")

    with pytest.raises(
        ServiceValidationError,
        match='Can not find heating curve "HC1"',
    ):
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

    assert translations["component.keba_keenergy.exceptions.cannot_find_heating_curve.message"] == expected


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "Duplicate outdoor temperature values found."),
        ("de", "Doppelte Außentemperatur-Werte gefunden."),
    ],
)
async def test_set_heating_curve_points_with_duplicate_outdoor_temperatures(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    language: str,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        HEATING_CURVES_RESPONSE_1_1,
        HEATING_CURVES_RESPONSE_2,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = language
    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="exceptions")

    with pytest.raises(
        ServiceValidationError,
        match="Duplicate outdoor temperature values found",
    ):
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_HEATING_CURVE_POINTS,
            service_data={
                ATTR_CONFIG_ENTRY: config_entry.entry_id,
                ATTR_HEATING_CURVE: "hc1",
                ATTR_POINTS: [
                    {"outdoor": 20, "flow": 35.30},
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

    assert translations["component.keba_keenergy.exceptions.duplicate_outdoor_temperature_values.message"] == expected


def test_away_date_range_schema_valid() -> None:
    data = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_START_DATE: "2026-01-01",
        ATTR_END_DATE: "2026-01-10",
    }

    AWAY_DATE_RANGE_SCHEMA(data)


def test_away_date_range_schema_missing_start() -> None:
    data = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_END_DATE: "2026-01-10",
    }

    with pytest.raises(vol.Invalid):
        AWAY_DATE_RANGE_SCHEMA(data)


def test_heating_curve_points_schema_valid() -> None:
    data: dict[str, Any] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_HEATING_CURVE: "hc1",
        ATTR_POINTS: [
            {"outdoor": -20, "flow": 35.3},
            {"outdoor": 0, "flow": 29.5},
        ],
    }

    HEATING_CURVE_POINTS_SCHEMA(data)


def test_heating_curve_points_schema_too_many_points() -> None:
    data: dict[str, Any] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_HEATING_CURVE: "hc1",
        ATTR_POINTS: [{"outdoor": i, "flow": i} for i in range(100)],
    }

    with pytest.raises(vol.Invalid):
        HEATING_CURVE_POINTS_SCHEMA(data)


def test_heating_curve_points_schema_invalid_curve() -> None:
    data: dict[str, Any] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_HEATING_CURVE: "INVALID",
        ATTR_POINTS: [{"outdoor": 0, "flow": 30}],
    }

    with pytest.raises(vol.Invalid):
        HEATING_CURVE_POINTS_SCHEMA(data)
