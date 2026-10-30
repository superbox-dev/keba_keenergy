# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the actions."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import Any

import probatio
import pytest
from homeassistant.core import State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.exceptions import ServiceValidationError

from custom_components.keba_keenergy.const import ATTR_CONFIG_ENTRY
from custom_components.keba_keenergy.const import ATTR_END_DATE
from custom_components.keba_keenergy.const import ATTR_HEATING_CURVE
from custom_components.keba_keenergy.const import ATTR_POINTS
from custom_components.keba_keenergy.const import ATTR_START_DATE
from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import HEATING_CURVE_POINTS_SCHEMA
from custom_components.keba_keenergy.const import SERVICE_SET_AWAY_DATE_RANGE
from custom_components.keba_keenergy.const import SERVICE_SET_HEATING_CURVE_POINTS
from custom_components.keba_keenergy.services import AWAY_DATE_RANGE_SCHEMA
from tests import init_translations
from tests.api_data import CURVE_NAMES_RESPONSE
from tests.api_data import CURVES_RENAMED_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_RESPONSE
from tests.api_data import get_curve_points_response
from tests.api_data import get_multiple_devices_fixed_data_response

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


async def test_set_away_range(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the action to set the away date range."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

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


async def test_set_unchanged_away_range(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the away date range is not written if the heating circuits already have it."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=DOMAIN,
        service=SERVICE_SET_AWAY_DATE_RANGE,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_START_DATE: "2026-01-22",
            ATTR_END_DATE: "2026-01-22",
        },
        blocking=True,
    )

    assert fake_api.write_requests() == []


async def test_set_away_range_with_invalid_start_and_end_date(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the action to set the away date range with an end date before the start date."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    hass.config.language = "de"
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="exceptions")

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


@pytest.mark.parametrize("language", ["en", "de"], indirect=True, ids=["en", "de"])
@pytest.mark.usefixtures("language")
async def test_set_away_range_with_invalid_config_entry(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the action to set the away date range with an unknown config entry."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="exceptions")

    with pytest.raises(ServiceValidationError, match=r"Invalid integration provided\. Got invalid"):
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

    assert translations["component.keba_keenergy.exceptions.invalid_config_entry.message"] == snapshot


@pytest.mark.parametrize("language", ["en", "de"], indirect=True, ids=["en", "de"])
@pytest.mark.usefixtures("language")
async def test_set_away_range_with_unloaded_config_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the action to set the away date range with an unloaded config entry."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="exceptions")

    # Unload the config entry.
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError, match="is not loaded"):
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

    assert translations["component.keba_keenergy.exceptions.unloaded_config_entry.message"] == snapshot


async def test_set_heating_curve_points(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the action to set the points of a heating curve."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=DOMAIN,
        service=SERVICE_SET_HEATING_CURVE_POINTS,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_HEATING_CURVE: "HC1",
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
        '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].verCnt", "value": "192"}]',
    )


@pytest.mark.parametrize("language", ["en", "de"], indirect=True, ids=["en", "de"])
@pytest.mark.usefixtures("language")
async def test_set_heating_curve_points_with_invalid_heating_curve(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the action to set the points of an unknown heating curve."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()
    # The heating curve HC1 was renamed on the control unit after the setup.
    fake_api.curves = CURVES_RENAMED_RESPONSE
    translations: dict[str, str] = await init_translations(hass, category="exceptions")

    with pytest.raises(
        ServiceValidationError,
        match='Cannot find curve "HC1"',
    ):
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_HEATING_CURVE_POINTS,
            service_data={
                ATTR_CONFIG_ENTRY: config_entry.entry_id,
                ATTR_HEATING_CURVE: "HC1",
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

    assert translations["component.keba_keenergy.exceptions.cannot_find_curve.message"] == snapshot


@pytest.mark.parametrize("language", ["en", "de"], indirect=True, ids=["en", "de"])
@pytest.mark.usefixtures("language")
async def test_set_heating_curve_points_with_duplicate_outdoor_temperatures(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the action to set heating curve points with duplicate outdoor temperatures."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="exceptions")

    with pytest.raises(
        ServiceValidationError,
        match="Duplicate outdoor temperature values found",
    ):
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_HEATING_CURVE_POINTS,
            service_data={
                ATTR_CONFIG_ENTRY: config_entry.entry_id,
                ATTR_HEATING_CURVE: "HC1",
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

    assert translations["component.keba_keenergy.exceptions.duplicate_outdoor_temperature_values.message"] == snapshot


def test_away_date_range_schema_valid() -> None:
    """Test the schema of the away date range action with valid data."""
    data: dict[str, str] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_START_DATE: "2026-01-01",
        ATTR_END_DATE: "2026-01-10",
    }

    AWAY_DATE_RANGE_SCHEMA(data)


def test_away_date_range_schema_missing_start() -> None:
    """Test the schema of the away date range action without a start date."""
    data: dict[str, str] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_END_DATE: "2026-01-10",
    }

    with pytest.raises(probatio.Invalid, match="required key not provided at 'start_date'"):
        AWAY_DATE_RANGE_SCHEMA(data)


def test_heating_curve_points_schema_valid() -> None:
    """Test the schema of the heating curve points action with valid data."""
    data: dict[str, Any] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_HEATING_CURVE: "HC1",
        ATTR_POINTS: [
            {"outdoor": -20, "flow": 35.3},
            {"outdoor": 0, "flow": 29.5},
        ],
    }

    HEATING_CURVE_POINTS_SCHEMA(data)


def test_heating_curve_points_schema_too_many_points() -> None:
    """Test the schema of the heating curve points action with more than 16 otherwise valid points."""
    data: dict[str, Any] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_HEATING_CURVE: "HC1",
        ATTR_POINTS: [{"outdoor": outdoor, "flow": 30} for outdoor in range(-20, -3)],
    }

    with pytest.raises(probatio.Invalid, match="length of value must be at most 16"):
        HEATING_CURVE_POINTS_SCHEMA(data)


def test_heating_curve_points_schema_without_points() -> None:
    """Test the schema of the heating curve points action with an empty list of points."""
    data: dict[str, Any] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_HEATING_CURVE: "HC1",
        ATTR_POINTS: [],
    }

    with pytest.raises(probatio.Invalid, match="length of value must be at least 1"):
        HEATING_CURVE_POINTS_SCHEMA(data)


def test_heating_curve_points_schema_invalid_curve() -> None:
    """Test the schema of the heating curve points action with an invalid heating curve name."""
    data: dict[str, Any] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_HEATING_CURVE: "INVALID",
        ATTR_POINTS: [{"outdoor": 0, "flow": 30}],
    }

    with pytest.raises(probatio.Invalid, match="does not match the expected pattern at 'heating_curve'"):
        HEATING_CURVE_POINTS_SCHEMA(data)


async def test_set_away_range_with_date_and_time(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the action to set the away date range only uses the date of a date with time."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=DOMAIN,
        service=SERVICE_SET_AWAY_DATE_RANGE,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_START_DATE: "2025-01-01T08:00:00",
            ATTR_END_DATE: "2025-01-14T20:00:00+00:00",
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.start", "value": "1735686000"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.start", "value": "1735686000"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.stop", "value": "1736895599"}, '
        '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.stop", "value": "1736895599"}]',
    )


def test_away_date_range_schema_invalid_date() -> None:
    """Test the schema of the away date range action with an invalid date."""
    data: dict[str, str] = {
        ATTR_CONFIG_ENTRY: "1234",
        ATTR_START_DATE: "2026-02-30",
        ATTR_END_DATE: "2026-03-10",
    }

    with pytest.raises(probatio.Invalid, match="Invalid datetime specified: 2026-02-30 at 'start_date'"):
        AWAY_DATE_RANGE_SCHEMA(data)


async def test_set_heating_curve_points_with_communication_error(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a communication error while reading the heating curves raises a translated error."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()
    fake_api.curves = HTTPStatus.BAD_REQUEST

    with pytest.raises(HomeAssistantError) as error:
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_HEATING_CURVE_POINTS,
            service_data={
                ATTR_CONFIG_ENTRY: config_entry.entry_id,
                ATTR_HEATING_CURVE: "HC1",
                ATTR_POINTS: [{"outdoor": 0, "flow": 30}],
            },
            blocking=True,
        )

    assert error.value.translation_key == "communication_error"
    assert fake_api.write_requests() == []


async def test_set_unchanged_heating_curve_points(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the action does not write the points if the heating curve already has them (flash writes)."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()
    fake_api.curves = [
        CURVE_NAMES_RESPONSE,
        get_curve_points_response(points=(("-20", "35.299999"), ("0", "29.5"), ("20", "23.9"))),
    ]

    await hass.services.async_call(
        domain=DOMAIN,
        service=SERVICE_SET_HEATING_CURVE_POINTS,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_HEATING_CURVE: "HC1",
            ATTR_POINTS: [
                {"outdoor": 20, "flow": 23.9},
                {"outdoor": -20, "flow": 35.3},
                {"outdoor": 0, "flow": 29.5},
            ],
        },
        blocking=True,
    )

    assert fake_api.write_requests() == []


async def test_set_heating_curve_points_updates_sensor(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the sensor of the heating curve in use shows the written points without another update."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=DOMAIN,
        service=SERVICE_SET_HEATING_CURVE_POINTS,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_HEATING_CURVE: "HC6",
            ATTR_POINTS: [
                {"outdoor": 20, "flow": 23.9},
                {"outdoor": -20, "flow": 35.3},
            ],
        },
        blocking=True,
    )

    state: State | None = hass.states.get("sensor.keba_keenergy_12345678_heat_circuit_heating_curve_1")

    assert isinstance(state, State)
    assert state.state == "HC6"
    assert state.attributes["points"] == [{"outdoor": -20, "flow": 35.3}, {"outdoor": 20, "flow": 23.9}]
