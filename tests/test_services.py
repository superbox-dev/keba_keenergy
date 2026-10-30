# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the actions."""

from __future__ import annotations

import re
from http import HTTPStatus
from typing import TYPE_CHECKING

import probatio
import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.keba_keenergy.const import ATTR_CONFIG_ENTRY
from custom_components.keba_keenergy.const import ATTR_END_DATE
from custom_components.keba_keenergy.const import ATTR_HEATING_CURVE
from custom_components.keba_keenergy.const import ATTR_POINTS
from custom_components.keba_keenergy.const import ATTR_START_DATE
from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import SERVICE_SET_AWAY_DATE_RANGE
from custom_components.keba_keenergy.const import SERVICE_SET_HEATING_CURVE_POINTS
from tests.api_data import CURVE_NAMES_RESPONSE
from tests.api_data import CURVES_RENAMED_RESPONSE
from tests.api_data import CURVES_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import Response
from tests.api_data import get_curve_points_response
from tests.api_data import get_multiple_devices_responses
from tests.test_services_data import AWAY_DATE_RANGE_WRITE
from tests.test_services_data import HEATING_CURVE_POINTS
from tests.test_services_data import HEATING_CURVE_POINTS_WRITE

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    ("start_date", "end_date"),
    [("2025-01-01", "2025-01-14"), ("2025-01-01T08:00:00", "2025-01-14T20:00:00+00:00")],
    ids=["date", "date_and_time"],
)
async def test_set_away_range(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    start_date: str,
    end_date: str,
) -> None:
    """Test the action to set the away date range, which only uses the date of a date with time."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=DOMAIN,
        service=SERVICE_SET_AWAY_DATE_RANGE,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_START_DATE: start_date,
            ATTR_END_DATE: end_date,
        },
        blocking=True,
    )

    assert fake_api.write_requests() == [AWAY_DATE_RANGE_WRITE]


async def test_set_unchanged_away_range(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the away date range is not written if the heating circuits already have it."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
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


async def test_set_same_away_range_twice(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the same away date range is written once, also before the next update."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
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

    assert fake_api.write_requests() == [AWAY_DATE_RANGE_WRITE]


@pytest.mark.parametrize(
    ("service_data", "expected_translation_key"),
    [
        (
            {ATTR_START_DATE: "2025-01-14", ATTR_END_DATE: "2025-01-01"},
            "end_date_smaller_than_start_date",
        ),
        (
            {ATTR_CONFIG_ENTRY: "invalid", ATTR_START_DATE: "2025-01-01", ATTR_END_DATE: "2025-01-14"},
            "invalid_config_entry",
        ),
    ],
    ids=["end_date_before_start_date", "invalid_config_entry"],
)
async def test_set_away_range_invalid(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    service_data: dict[str, str],
    expected_translation_key: str,
) -> None:
    """Test that the action to set the away date range rejects invalid data with a translated error."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    with pytest.raises(ServiceValidationError) as error:
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_AWAY_DATE_RANGE,
            service_data={ATTR_CONFIG_ENTRY: config_entry.entry_id, **service_data},
            blocking=True,
        )

    assert error.value.translation_key == expected_translation_key
    assert fake_api.write_requests() == []


async def test_set_away_range_with_unloaded_config_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the action to set the away date range with an unloaded config entry."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()
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


async def test_set_away_range_with_config_entry_of_other_integration(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the action rejects a loaded config entry of another integration."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()
    other_entry: MockConfigEntry = MockConfigEntry(domain="other", state=ConfigEntryState.LOADED)
    other_entry.add_to_hass(hass)

    with pytest.raises(ServiceValidationError) as error:
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_AWAY_DATE_RANGE,
            service_data={
                ATTR_CONFIG_ENTRY: other_entry.entry_id,
                ATTR_START_DATE: "2025-01-01",
                ATTR_END_DATE: "2025-01-14",
            },
            blocking=True,
        )

    assert error.value.translation_key == "invalid_config_entry"
    assert fake_api.write_requests() == []


@pytest.mark.parametrize(
    ("service_data", "expected"),
    [
        ({ATTR_END_DATE: "2026-01-10"}, "required key not provided at 'start_date'"),
        (
            {ATTR_START_DATE: "2026-02-30", ATTR_END_DATE: "2026-03-10"},
            "Invalid datetime specified: 2026-02-30 at 'start_date'",
        ),
    ],
    ids=["missing_start_date", "invalid_date"],
)
async def test_set_away_range_invalid_data(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    service_data: dict[str, str],
    expected: str,
) -> None:
    """Test that the schema of the action to set the away date range rejects invalid data."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    with pytest.raises(probatio.Invalid, match=re.escape(expected)):
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_AWAY_DATE_RANGE,
            service_data={ATTR_CONFIG_ENTRY: config_entry.entry_id, **service_data},
            blocking=True,
        )


async def test_set_heating_curve_points(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test the action to set the points of a heating curve, the points are written sorted."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=DOMAIN,
        service=SERVICE_SET_HEATING_CURVE_POINTS,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_HEATING_CURVE: "HC1",
            ATTR_POINTS: HEATING_CURVE_POINTS,
        },
        blocking=True,
    )

    assert fake_api.write_requests() == [HEATING_CURVE_POINTS_WRITE]


@pytest.mark.parametrize(
    ("curves_and_points", "expected_translation_key"),
    [
        ((CURVES_RENAMED_RESPONSE, HEATING_CURVE_POINTS), "cannot_find_curve"),
        (
            (CURVES_RESPONSE, [{"outdoor": 20, "flow": 35.3}, *HEATING_CURVE_POINTS[1:]]),
            "duplicate_outdoor_temperature_values",
        ),
        # The outdoor temperatures are rounded to two decimals.
        (
            (CURVES_RESPONSE, [{"outdoor": -20.001, "flow": 35.3}, {"outdoor": -20.004, "flow": 30}]),
            "duplicate_outdoor_temperature_values",
        ),
    ],
    ids=["renamed_curve", "duplicate_outdoor_temperatures", "duplicate_outdoor_temperatures_after_rounding"],
)
async def test_set_heating_curve_points_invalid(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    curves_and_points: tuple[list[Response], list[dict[str, float]]],
    expected_translation_key: str,
) -> None:
    """Test that the action to set the points of a heating curve rejects invalid points or curves."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()
    # E.g. the heating curve HC1 was renamed on the control unit after the setup.
    fake_api.curves, points = curves_and_points

    with pytest.raises(ServiceValidationError) as error:
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_HEATING_CURVE_POINTS,
            service_data={
                ATTR_CONFIG_ENTRY: config_entry.entry_id,
                ATTR_HEATING_CURVE: "HC1",
                ATTR_POINTS: points,
            },
            blocking=True,
        )

    assert error.value.translation_key == expected_translation_key
    assert fake_api.write_requests() == []


@pytest.mark.parametrize(
    ("service_data", "expected"),
    [
        (
            {ATTR_HEATING_CURVE: "HC1", ATTR_POINTS: [{"outdoor": outdoor, "flow": 30} for outdoor in range(-20, -3)]},
            "length of value must be at most 16",
        ),
        ({ATTR_HEATING_CURVE: "HC1", ATTR_POINTS: []}, "length of value must be at least 1"),
        (
            {ATTR_HEATING_CURVE: "INVALID", ATTR_POINTS: [{"outdoor": 0, "flow": 30}]},
            "does not match the expected pattern at 'heating_curve'",
        ),
        (
            {ATTR_HEATING_CURVE: "HC1", ATTR_POINTS: [{"outdoor": -41, "flow": 30}]},
            "value must be at least -40 at 'points[0].outdoor'",
        ),
        (
            {ATTR_HEATING_CURVE: "HC1", ATTR_POINTS: [{"outdoor": 41, "flow": 30}]},
            "value must be at most 40 at 'points[0].outdoor'",
        ),
        (
            {ATTR_HEATING_CURVE: "HC1", ATTR_POINTS: [{"outdoor": 0, "flow": 9}]},
            "value must be at least 10 at 'points[0].flow'",
        ),
        (
            {ATTR_HEATING_CURVE: "HC1", ATTR_POINTS: [{"outdoor": 0, "flow": 91}]},
            "value must be at most 90 at 'points[0].flow'",
        ),
    ],
    ids=[
        "too_many_points",
        "without_points",
        "invalid_curve",
        "outdoor_too_low",
        "outdoor_too_high",
        "flow_too_low",
        "flow_too_high",
    ],
)
async def test_set_heating_curve_points_invalid_data(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    service_data: dict[str, object],
    expected: str,
) -> None:
    """Test that the schema of the action to set the points of a heating curve rejects invalid data."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    with pytest.raises(probatio.Invalid, match=re.escape(expected)):
        await hass.services.async_call(
            domain=DOMAIN,
            service=SERVICE_SET_HEATING_CURVE_POINTS,
            service_data={ATTR_CONFIG_ENTRY: config_entry.entry_id, **service_data},
            blocking=True,
        )


async def test_set_heating_curve_points_with_communication_error(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a communication error while reading the heating curves raises a translated error."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
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
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
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
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
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
