# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the write counter and the repair issues."""

from __future__ import annotations

from datetime import date
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any

import pytest
from homeassistant.components.water_heater import ATTR_OPERATION_MODE
from homeassistant.components.water_heater import SERVICE_SET_OPERATION_MODE
from homeassistant.components.water_heater.const import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.components.water_heater.const import STATE_PERFORMANCE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.keba_keenergy.const import ATTR_CONFIG_ENTRY
from custom_components.keba_keenergy.const import ATTR_END_DATE
from custom_components.keba_keenergy.const import ATTR_HEATING_CURVE
from custom_components.keba_keenergy.const import ATTR_POINTS
from custom_components.keba_keenergy.const import ATTR_START_DATE
from custom_components.keba_keenergy.const import ATTR_WRITES
from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import FLASH_WRITE_ISSUE_ID
from custom_components.keba_keenergy.const import FLASH_WRITE_LIMIT_PER_WEEK
from custom_components.keba_keenergy.const import SERVICE_SET_AWAY_DATE_RANGE
from custom_components.keba_keenergy.const import SERVICE_SET_HEATING_CURVE_POINTS
from tests import fire_debounced_writes
from tests import get_state
from tests import init_translations
from tests import select_option
from tests import set_number_value
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE
from tests.api_data import get_multiple_devices_responses
from tests.test_issues_data import STORED_WRITES
from tests.test_issues_data import WRITE_COUNT_ENTITY_ID
from tests.test_issues_data import WRITES_PER_VALUE
from tests.test_issues_data import get_issue_id
from tests.test_issues_data import get_store
from tests.test_issues_data import get_store_key
from tests.test_issues_data import get_week

if TYPE_CHECKING:
    from datetime import datetime

    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("language")
async def test_flash_write_issue(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    snapshot: SnapshotAssertion,
) -> None:
    """Test the repair issue for frequent write operations of a control unit, with its translated texts."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    key: str = get_store_key(config_entry.entry_id)
    hass_storage[key] = get_store(key, {"week": get_week(dt_util.now().date()), "count": FLASH_WRITE_LIMIT_PER_WEEK})
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="issues")

    await select_option(hass, "select.keba_keenergy_12345678_buffer_tank_operating_mode_1", "on")
    await select_option(hass, "select.keba_keenergy_12345678_buffer_tank_operating_mode_1", "off")

    issue: ir.IssueEntry | None = ir.async_get(hass).async_get_issue(DOMAIN, get_issue_id(config_entry.entry_id))
    assert issue is not None

    translation_key: str = f"component.keba_keenergy.issues.{issue.translation_key}"
    placeholders: dict[str, str] = issue.translation_placeholders or {}

    assert issue == snapshot(name="issue")
    assert {
        "title": translations[f"{translation_key}.title"],
        # The paragraphs of the description, a snapshot of the text would indent its empty lines.
        "description": translations[f"{translation_key}.description"].format(**placeholders).split("\n\n"),
    } == snapshot(name="translations")


async def test_issue_after_restart(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that the repair issue is created on setup if the stored counter of this week exceeds the limit.

    Home Assistant does not restore the issue after a restart, because it is not persistent.
    """
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    key: str = get_store_key(config_entry.entry_id)
    hass_storage[key] = get_store(
        key,
        {"week": get_week(dt_util.now().date()), "count": FLASH_WRITE_LIMIT_PER_WEEK + 5, "writes": STORED_WRITES},
    )
    await fake_api.setup_integration()

    issue: ir.IssueEntry | None = ir.async_get(hass).async_get_issue(DOMAIN, get_issue_id(config_entry.entry_id))

    assert issue is not None
    assert issue.active


async def test_ignored_write_is_not_counted(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that a write that is not counted (heat up the hot water tank) keeps the weekly write counter."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE)
    key: str = get_store_key(config_entry.entry_id)
    counter: dict[str, Any] = {
        "week": get_week(dt_util.now().date()),
        "count": 5,
        "writes": STORED_WRITES,
    }
    hass_storage[key] = get_store(key, counter)
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

    state: State = get_state(hass, WRITE_COUNT_ENTITY_ID)

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode", "value": "3"}]',
    ]
    assert hass_storage[key]["data"]["flash_write_counter"] == counter
    assert state.state == "5"
    assert state.attributes[ATTR_WRITES] == STORED_WRITES


async def test_write_counter_reset_at_midnight_of_new_week(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that the write counter resets at midnight of a new week, without an update or a write."""
    fake_api.responses = get_multiple_devices_responses(
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # The polling at midnight.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    )
    freezer.move_to(dt_util.start_of_local_day(date(2026, 3, 8)) + timedelta(hours=12))
    key: str = get_store_key(config_entry.entry_id)
    hass_storage[key] = get_store(key, {"week": get_week(date(2026, 3, 8)), "count": 5, "writes": STORED_WRITES})
    await fake_api.setup_integration()

    # Midnight of Tuesday, 2026-03-10: 2026-03-08 is the Sunday of the previous week, 2026-03-09 the Monday of the same.
    midnight: datetime = dt_util.start_of_local_day(date(2026, 3, 10))
    freezer.move_to(midnight)
    async_fire_time_changed(hass, midnight)
    await hass.async_block_till_done()

    state: State = get_state(hass, WRITE_COUNT_ENTITY_ID)

    assert hass_storage[key]["data"]["flash_write_counter"] == {
        "week": get_week(midnight.date()),
        "count": 0,
        "writes": {},
    }
    assert state.state == "0"
    assert state.attributes[ATTR_WRITES] == {}


async def test_write_counter_kept_at_midnight_of_same_week(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that the write counter is kept at midnight within the same week."""
    fake_api.responses = get_multiple_devices_responses(
        MULTIPLE_DEVICES_DATA_RESPONSE,
        # The polling at midnight.
        MULTIPLE_DEVICES_DATA_RESPONSE,
    )
    freezer.move_to(dt_util.start_of_local_day(date(2026, 3, 9)) + timedelta(hours=12))
    key: str = get_store_key(config_entry.entry_id)
    hass_storage[key] = get_store(key, {"week": get_week(date(2026, 3, 9)), "count": 5, "writes": STORED_WRITES})
    await fake_api.setup_integration()

    # Midnight of Tuesday, 2026-03-10: 2026-03-08 is the Sunday of the previous week, 2026-03-09 the Monday of the same.
    midnight: datetime = dt_util.start_of_local_day(date(2026, 3, 10))
    freezer.move_to(midnight)
    async_fire_time_changed(hass, midnight)
    await hass.async_block_till_done()

    state: State = get_state(hass, WRITE_COUNT_ENTITY_ID)

    assert hass_storage[key]["data"]["flash_write_counter"] == {
        "week": get_week(midnight.date()),
        "count": 5,
        "writes": STORED_WRITES,
    }
    assert state.state == "5"
    assert state.attributes[ATTR_WRITES] == STORED_WRITES


async def test_write_in_new_year_week_resets_write_counter(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that the first write in a new week resets the write counter before it counts, also without the timer.

    Sunday, 2027-01-03, is in the ISO week 53 of 2026, Monday, 2027-01-04, in the week 1 of 2027.
    """
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    freezer.move_to(dt_util.start_of_local_day(date(2027, 1, 3)) + timedelta(hours=12))
    key: str = get_store_key(config_entry.entry_id)
    hass_storage[key] = get_store(key, {"week": [2026, 53], "count": 5, "writes": STORED_WRITES})
    await fake_api.setup_integration()

    # The time changes without the timer at midnight, e.g. while Home Assistant was suspended.
    freezer.move_to(dt_util.start_of_local_day(date(2027, 1, 4)) + timedelta(hours=12))
    await select_option(hass, "select.keba_keenergy_12345678_buffer_tank_operating_mode_1", "on")

    assert hass_storage[key]["data"]["flash_write_counter"] == {
        "week": [2027, 1],
        "count": 1,
        "writes": {"buffer_tank_1.operating_mode": 1},
    }


async def test_write_counter_after_unload(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that the write counter no longer resets at midnight after the integration is unloaded."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    freezer.move_to(dt_util.start_of_local_day(date(2026, 3, 8)) + timedelta(hours=12))
    key: str = get_store_key(config_entry.entry_id)
    counter: dict[str, Any] = {"week": get_week(date(2026, 3, 8)), "count": 5, "writes": STORED_WRITES}
    hass_storage[key] = get_store(key, counter)
    await fake_api.setup_integration()
    await hass.config_entries.async_unload(config_entry.entry_id)

    midnight: datetime = dt_util.start_of_local_day(date(2026, 3, 9))
    freezer.move_to(midnight)
    async_fire_time_changed(hass, midnight)
    await hass.async_block_till_done()

    assert hass_storage[key]["data"]["flash_write_counter"] == counter


@pytest.mark.parametrize(
    "stored_week_offset",
    [timedelta(weeks=-1), timedelta(weeks=1)],
    ids=["previous_week", "future_week"],
)
async def test_new_week_resets_write_counter(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    stored_week_offset: timedelta,
) -> None:
    """Test that the setup in another week resets the write counter and removes the repair issue, without a write.

    A stored week in the future, e.g. after the clock was set back, is another week as well.
    """
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    today: date = dt_util.now().date()
    key: str = get_store_key(config_entry.entry_id)
    hass_storage[key] = get_store(
        key,
        {
            "week": get_week(today + stored_week_offset),
            "count": FLASH_WRITE_LIMIT_PER_WEEK + 1,
            "writes": {"system.operating_mode": FLASH_WRITE_LIMIT_PER_WEEK + 1},
        },
    )
    ir.async_create_issue(
        hass,
        domain=DOMAIN,
        issue_id=get_issue_id(config_entry.entry_id),
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=FLASH_WRITE_ISSUE_ID,
    )
    await fake_api.setup_integration()

    state: State = get_state(hass, WRITE_COUNT_ENTITY_ID)

    assert fake_api.write_requests() == []
    assert ir.async_get(hass).async_get_issue(DOMAIN, get_issue_id(config_entry.entry_id)) is None
    assert hass_storage[key]["data"]["flash_write_counter"] == {"week": get_week(today), "count": 0, "writes": {}}
    assert state.state == "0"
    assert state.attributes[ATTR_WRITES] == {}


async def test_shared_write_counter_is_removed(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that the write counter and the repair issue shared by all control units in older versions are removed."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    hass_storage[DOMAIN] = get_store(DOMAIN, {"week": get_week(dt_util.now().date()), "count": 7})
    ir.async_create_issue(
        hass,
        domain=DOMAIN,
        issue_id=FLASH_WRITE_ISSUE_ID,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=FLASH_WRITE_ISSUE_ID,
    )
    await fake_api.setup_integration()

    state: State = get_state(hass, WRITE_COUNT_ENTITY_ID)

    assert DOMAIN not in hass_storage
    assert ir.async_get(hass).async_get_issue(DOMAIN, FLASH_WRITE_ISSUE_ID) is None
    assert state.state == "0"
    assert state.attributes[ATTR_WRITES] == {}


async def test_writes_per_value(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that each written value is counted, a write of several values counts once in total."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    await select_option(hass, "select.keba_keenergy_12345678_operating_mode", "auto")
    await select_option(hass, "select.keba_keenergy_12345678_buffer_tank_operating_mode_2", "off")

    await set_number_value(hass, "number.keba_keenergy_12345678_solar_circuit_target_temperature_1_2", 50)
    await fire_debounced_writes(hass)

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

    state: State = get_state(hass, WRITE_COUNT_ENTITY_ID)

    assert hass_storage[get_store_key(config_entry.entry_id)]["data"]["flash_write_counter"] == {
        "week": get_week(dt_util.now().date()),
        "count": 5,
        "writes": WRITES_PER_VALUE,
    }
    assert state.state == "5"
    assert state.attributes[ATTR_WRITES] == WRITES_PER_VALUE


async def test_remove_entry_removes_write_counter(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that removing a config entry removes its write counter."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    key: str = get_store_key(config_entry.entry_id)
    hass_storage[key] = get_store(key, {"week": get_week(dt_util.now().date()), "count": 1})
    await fake_api.setup_integration()

    await hass.config_entries.async_remove(config_entry.entry_id)
    await hass.async_block_till_done()

    assert key not in hass_storage
