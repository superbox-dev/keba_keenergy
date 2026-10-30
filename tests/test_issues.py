# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the write counter and the repair issues."""

from __future__ import annotations

from datetime import date
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any

import pytest
from homeassistant.components.number import ATTR_VALUE
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number.const import SERVICE_SET_VALUE
from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.components.water_heater import ATTR_OPERATION_MODE
from homeassistant.components.water_heater import SERVICE_SET_OPERATION_MODE
from homeassistant.components.water_heater.const import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.components.water_heater.const import STATE_PERFORMANCE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import State
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.keba_keenergy.const import ATTR_CONFIG_ENTRY
from custom_components.keba_keenergy.const import ATTR_END_DATE
from custom_components.keba_keenergy.const import ATTR_HEATING_CURVE
from custom_components.keba_keenergy.const import ATTR_POINTS
from custom_components.keba_keenergy.const import ATTR_START_DATE
from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import FLASH_WRITE_DELAY
from custom_components.keba_keenergy.const import FLASH_WRITE_ISSUE_ID
from custom_components.keba_keenergy.const import FLASH_WRITE_LIMIT_PER_WEEK
from custom_components.keba_keenergy.const import SERVICE_SET_AWAY_DATE_RANGE
from custom_components.keba_keenergy.const import SERVICE_SET_HEATING_CURVE_POINTS
from tests import init_translations
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_RESPONSE
from tests.api_data import get_multiple_devices_fixed_data_response
from tests.test_issues_data import ISSUE_DESCRIPTION_DE
from tests.test_issues_data import ISSUE_DESCRIPTION_EN
from tests.test_issues_data import WRITE_COUNT_ENTITY_ID
from tests.test_issues_data import WRITES_PER_VALUE

if TYPE_CHECKING:
    from datetime import datetime

    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from tests.conftest import FakeKebaKeEnergyAPI


def _week(day: date, /) -> list[int]:
    return [day.isocalendar().year, day.isocalendar().week]


def _store(key: str, counter: dict[str, Any], /) -> dict[str, Any]:
    return {
        "version": 1,
        "minor_version": 1,
        "key": key,
        "data": {"flash_write_counter": counter},
    }


def _issue_id(config_entry: MockConfigEntry, /) -> str:
    return f"{FLASH_WRITE_ISSUE_ID}_{config_entry.entry_id}"


async def _select_option(hass: HomeAssistant, entity_id: str, option: str, /) -> None:
    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_OPTION: option,
        },
        blocking=True,
    )


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", ("Frequent write operations detected", ISSUE_DESCRIPTION_EN)),
        ("de", ("Viele Schreibzugriffe erkannt", ISSUE_DESCRIPTION_DE)),
    ],
    indirect=["language"],
    ids=["en", "de"],
)
@pytest.mark.usefixtures("language")
async def test_issues(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    expected: tuple[str, str],
) -> None:
    """Test the repair issue for frequent write operations of a control unit."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the first action call.
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # Read the API after the second action call.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    key: str = f"{DOMAIN}.{config_entry.entry_id}"
    hass_storage[key] = _store(key, {"week": _week(dt_util.now().date()), "count": FLASH_WRITE_LIMIT_PER_WEEK})
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="issues")

    await _select_option(hass, "select.keba_keenergy_12345678_buffer_tank_operating_mode_1", "on")
    await _select_option(hass, "select.keba_keenergy_12345678_buffer_tank_operating_mode_1", "off")

    issue: ir.IssueEntry | None = ir.async_get(hass).async_get_issue(DOMAIN, _issue_id(config_entry))

    assert issue is not None
    assert issue.severity == ir.IssueSeverity.WARNING

    title: str = translations[f"component.keba_keenergy.issues.{issue.translation_key}.title"]
    description: str = translations[f"component.keba_keenergy.issues.{issue.translation_key}.description"].format(
        **(issue.translation_placeholders or {}),
    )

    assert (title, description) == expected


async def test_ignored_write_is_not_counted(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that a write that is not counted (heat up the hot water tank) keeps the weekly write counter."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
    ]
    key: str = f"{DOMAIN}.{config_entry.entry_id}"
    counter: dict[str, Any] = {"week": _week(dt_util.now().date()), "count": 5, "writes": {"system.operating_mode": 5}}
    hass_storage[key] = _store(key, counter)
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_OPERATION_MODE,
        service_data={
            ATTR_ENTITY_ID: "water_heater.keba_keenergy_12345678_1",
            ATTR_OPERATION_MODE: STATE_PERFORMANCE,
        },
        blocking=True,
    )

    state: State | None = hass.states.get(WRITE_COUNT_ENTITY_ID)

    assert len(fake_api.write_requests()) == 1
    assert hass_storage[key]["data"]["flash_write_counter"] == counter
    assert isinstance(state, State)
    assert state.state == "5"
    assert state.attributes["writes"] == {"system.operating_mode": 5}


@pytest.mark.parametrize(
    ("setup_day", "expected_writes"),
    [
        (date(2026, 3, 8), {}),
        (date(2026, 3, 9), {"system.operating_mode": 5}),
    ],
    ids=["new_week", "same_week"],
)
async def test_write_counter_at_midnight(
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    freezer: FrozenDateTimeFactory,
    setup_day: date,
    expected_writes: dict[str, int],
) -> None:
    """Test that the write counter resets at midnight of a new week only, without an update or a write."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # The polling at midnight.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    freezer.move_to(dt_util.start_of_local_day(setup_day) + timedelta(hours=12))
    key: str = f"{DOMAIN}.{fake_api.config_entry.entry_id}"
    hass_storage[key] = _store(key, {"week": _week(setup_day), "count": 5, "writes": {"system.operating_mode": 5}})
    await fake_api.setup_integration()

    # Midnight of Tuesday, 2026-03-10: 2026-03-08 is the Sunday of the previous week, 2026-03-09 the Monday of the same.
    midnight: datetime = dt_util.start_of_local_day(date(2026, 3, 10))
    freezer.move_to(midnight)
    async_fire_time_changed(fake_api.hass, midnight)
    await fake_api.hass.async_block_till_done()

    state: State | None = fake_api.hass.states.get(WRITE_COUNT_ENTITY_ID)
    expected_count: int = sum(expected_writes.values())

    assert hass_storage[key]["data"]["flash_write_counter"] == {
        "week": _week(midnight.date()),
        "count": expected_count,
        "writes": expected_writes,
    }
    assert isinstance(state, State)
    assert state.state == str(expected_count)
    assert state.attributes["writes"] == expected_writes


async def test_write_counter_after_unload(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that the write counter no longer resets at midnight after the integration is unloaded."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    freezer.move_to(dt_util.start_of_local_day(date(2026, 3, 8)) + timedelta(hours=12))
    key: str = f"{DOMAIN}.{fake_api.config_entry.entry_id}"
    counter: dict[str, Any] = {"week": _week(date(2026, 3, 8)), "count": 5, "writes": {"system.operating_mode": 5}}
    hass_storage[key] = _store(key, counter)
    await fake_api.setup_integration()
    await hass.config_entries.async_unload(fake_api.config_entry.entry_id)

    midnight: datetime = dt_util.start_of_local_day(date(2026, 3, 9))
    freezer.move_to(midnight)
    async_fire_time_changed(hass, midnight)
    await hass.async_block_till_done()

    assert hass_storage[key]["data"]["flash_write_counter"] == counter


async def test_new_week_resets_write_counter(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that an update in a new week resets the write counter and removes the repair issue, without a write."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    today: date = dt_util.now().date()
    key: str = f"{DOMAIN}.{config_entry.entry_id}"
    hass_storage[key] = _store(
        key,
        {
            "week": _week(today - timedelta(weeks=1)),
            "count": FLASH_WRITE_LIMIT_PER_WEEK + 1,
            "writes": {"system.operating_mode": FLASH_WRITE_LIMIT_PER_WEEK + 1},
        },
    )
    ir.async_create_issue(
        hass,
        domain=DOMAIN,
        issue_id=_issue_id(config_entry),
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=FLASH_WRITE_ISSUE_ID,
    )
    await fake_api.setup_integration()

    state: State | None = hass.states.get(WRITE_COUNT_ENTITY_ID)

    assert fake_api.write_requests() == []
    assert ir.async_get(hass).async_get_issue(DOMAIN, _issue_id(config_entry)) is None
    assert hass_storage[key]["data"]["flash_write_counter"] == {"week": _week(today), "count": 0, "writes": {}}
    assert isinstance(state, State)
    assert state.state == "0"
    assert state.attributes["writes"] == {}


async def test_shared_write_counter_is_removed(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that the write counter and the repair issue shared by all control units in older versions are removed."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    hass_storage[DOMAIN] = _store(DOMAIN, {"week": _week(dt_util.now().date()), "count": 7})
    ir.async_create_issue(
        hass,
        domain=DOMAIN,
        issue_id=FLASH_WRITE_ISSUE_ID,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=FLASH_WRITE_ISSUE_ID,
    )
    await fake_api.setup_integration()

    state: State | None = hass.states.get(WRITE_COUNT_ENTITY_ID)

    assert DOMAIN not in hass_storage
    assert ir.async_get(hass).async_get_issue(DOMAIN, FLASH_WRITE_ISSUE_ID) is None
    assert isinstance(state, State)
    assert state.state == "0"
    assert state.attributes["writes"] == {}


async def test_writes_per_value(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that each written value is counted, a write of several values counts once in total."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        # Read the API on setup and after each action call.
        *[MULTIPLE_DEVICES_DATA_RESPONSE] * 6,
    ]
    await fake_api.setup_integration()

    await _select_option(hass, "select.keba_keenergy_12345678_operating_mode", "auto")
    await _select_option(hass, "select.keba_keenergy_12345678_buffer_tank_operating_mode_2", "off")

    await hass.services.async_call(
        domain=NUMBER_DOMAIN,
        service=SERVICE_SET_VALUE,
        service_data={
            ATTR_ENTITY_ID: "number.keba_keenergy_12345678_solar_circuit_target_temperature_1_2",
            ATTR_VALUE: 50,
        },
        blocking=True,
    )
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=FLASH_WRITE_DELAY))
    await hass.async_block_till_done()

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
        service=SERVICE_SET_HEATING_CURVE_POINTS,
        service_data={
            ATTR_CONFIG_ENTRY: config_entry.entry_id,
            ATTR_HEATING_CURVE: "HC1",
            ATTR_POINTS: [{"outdoor": -20, "flow": 35}, {"outdoor": 20, "flow": 24}],
        },
        blocking=True,
    )

    state: State | None = hass.states.get(WRITE_COUNT_ENTITY_ID)

    assert hass_storage[f"{DOMAIN}.{config_entry.entry_id}"]["data"]["flash_write_counter"] == {
        "week": _week(dt_util.now().date()),
        "count": 5,
        "writes": WRITES_PER_VALUE,
    }
    assert isinstance(state, State)
    assert state.state == "5"
    assert state.attributes["writes"] == WRITES_PER_VALUE


async def test_remove_entry(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that removing a config entry removes its write counter."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        get_multiple_devices_fixed_data_response(),
        MULTIPLE_DEVICES_DATA_RESPONSE,
    ]
    key: str = f"{DOMAIN}.{config_entry.entry_id}"
    hass_storage[key] = _store(key, {"week": _week(dt_util.now().date()), "count": 1})
    await fake_api.setup_integration()

    await hass.config_entries.async_remove(config_entry.entry_id)
    await hass.async_block_till_done()

    assert key not in hass_storage
