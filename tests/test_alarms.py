# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the alarms of the control unit (repair issues, pending alarms sensor and alarm event)."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import Any

import pytest
from homeassistant.components.event import ATTR_EVENT_TYPE
from homeassistant.components.event import ATTR_EVENT_TYPES
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import async_capture_events

from custom_components.keba_keenergy.const import ATTR_ALARMS
from custom_components.keba_keenergy.const import DOMAIN
from tests import get_state
from tests import init_translations
from tests.api_data import HIGH_PRESSURE_ALARM
from tests.api_data import SENSOR_BREAK_ALARM
from tests.api_data import SINGLE_DEVICE_DATA_RESPONSE
from tests.api_data import AlarmValue
from tests.api_data import get_single_device_responses
from tests.test_alarms_data import ALARM_ENTITY_ID
from tests.test_alarms_data import HIGH_PRESSURE_ATTRIBUTES
from tests.test_alarms_data import PENDING_ALARMS
from tests.test_alarms_data import PENDING_ALARMS_ENTITY_ID
from tests.test_alarms_data import SENSOR_BREAK_ATTRIBUTES
from tests.test_alarms_data import AlarmAttributes
from tests.test_alarms_data import get_alarm_issue_id
from tests.test_alarms_data import get_alarm_store
from tests.test_alarms_data import get_alarm_store_key

if TYPE_CHECKING:
    from homeassistant.core import Event
    from homeassistant.core import EventStateChangedData
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from custom_components.keba_keenergy.coordinator import KebaKeEnergyDataUpdateCoordinator
    from tests.conftest import FakeKebaKeEnergyAPI


def get_alarm_events(events: list[Event[EventStateChangedData]], /) -> list[tuple[str, AlarmAttributes]]:
    """Return the event type and the alarm attributes of every alarm event, without the attributes of the entity."""
    return [
        (
            new_state.attributes[ATTR_EVENT_TYPE],
            {
                key: value
                for key, value in new_state.attributes.items()
                if key not in (ATTR_EVENT_TYPE, ATTR_EVENT_TYPES, ATTR_FRIENDLY_NAME)
            },
        )
        for event in events
        if event.data["entity_id"] == ALARM_ENTITY_ID
        # Like the triggers of Home Assistant, only a change of a written state is an event.
        and (new_state := event.data["new_state"]) is not None
        and (old_state := event.data["old_state"]) is not None
        and new_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
        and new_state.state != old_state.state
    ]


@pytest.mark.parametrize("alarm", [SENSOR_BREAK_ALARM, HIGH_PRESSURE_ALARM], ids=["sensor_break", "acknowledgeable"])
@pytest.mark.usefixtures("language")
async def test_alarm_issue(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    alarm: AlarmValue,
) -> None:
    """Test the repair issue of a pending alarm, with its translated texts."""
    fake_api.responses = get_single_device_responses()
    fake_api.alarms = [alarm]
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="issues")

    issue: ir.IssueEntry | None = ir.async_get(hass).async_get_issue(
        DOMAIN, get_alarm_issue_id(fake_api.config_entry.entry_id, alarm)
    )
    assert issue is not None

    translation_key: str = f"component.keba_keenergy.issues.{issue.translation_key}"
    placeholders: dict[str, str] = issue.translation_placeholders or {}

    assert issue == snapshot(name="issue")
    assert {
        "title": translations[f"{translation_key}.title"].format(**placeholders),
        # The paragraphs of the description, a snapshot of the text would indent its empty lines.
        "description": translations[f"{translation_key}.description"].format(**placeholders).split("\n\n"),
    } == snapshot(name="translations")


@pytest.mark.parametrize(
    ("priority", "severity"),
    [
        (0, ir.IssueSeverity.ERROR),
        (1, ir.IssueSeverity.ERROR),
        (2, ir.IssueSeverity.WARNING),
        (3, ir.IssueSeverity.WARNING),
        (7, ir.IssueSeverity.WARNING),
    ],
    ids=["emergency", "error", "warning", "info", "unknown"],
)
async def test_alarm_issue_severity(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    priority: int,
    severity: ir.IssueSeverity,
) -> None:
    """Test that emergencies and errors are errors and all other priorities are warnings, like the Web HMI."""
    fake_api.responses = get_single_device_responses()
    fake_api.alarms = [{**SENSOR_BREAK_ALARM, "prio": priority}]
    await fake_api.setup_integration()

    issue: ir.IssueEntry | None = ir.async_get(hass).async_get_issue(
        DOMAIN, get_alarm_issue_id(fake_api.config_entry.entry_id, SENSOR_BREAK_ALARM)
    )

    assert issue is not None
    assert issue.severity is severity


async def test_alarm_raised_and_cleared(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test the events, the repair issues, the sensor and the store when alarms are raised and cleared."""
    fake_api.responses = get_single_device_responses(SINGLE_DEVICE_DATA_RESPONSE, SINGLE_DEVICE_DATA_RESPONSE)
    await fake_api.setup_integration()
    coordinator: KebaKeEnergyDataUpdateCoordinator = fake_api.config_entry.runtime_data.data_coordinator
    entry_id: str = fake_api.config_entry.entry_id
    key: str = get_alarm_store_key(entry_id)
    events: list[Event[EventStateChangedData]] = async_capture_events(hass, EVENT_STATE_CHANGED)

    assert get_state(hass, ALARM_ENTITY_ID).state == STATE_UNKNOWN
    assert get_state(hass, PENDING_ALARMS_ENTITY_ID).state == "0"

    fake_api.alarms = [HIGH_PRESSURE_ALARM, SENSOR_BREAK_ALARM]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    sensor: State = get_state(hass, PENDING_ALARMS_ENTITY_ID)

    assert get_alarm_events(events) == [("raised", SENSOR_BREAK_ATTRIBUTES), ("raised", HIGH_PRESSURE_ATTRIBUTES)]
    assert sensor.state == "2"
    assert sensor.attributes[ATTR_ALARMS] == PENDING_ALARMS
    assert hass_storage[key]["data"] == {"alarms": [SENSOR_BREAK_ATTRIBUTES, HIGH_PRESSURE_ATTRIBUTES]}
    assert ir.async_get(hass).async_get_issue(DOMAIN, get_alarm_issue_id(entry_id, SENSOR_BREAK_ALARM)) is not None

    events.clear()
    fake_api.alarms = [HIGH_PRESSURE_ALARM]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert get_alarm_events(events) == [("cleared", SENSOR_BREAK_ATTRIBUTES)]
    assert get_state(hass, PENDING_ALARMS_ENTITY_ID).state == "1"
    assert hass_storage[key]["data"] == {"alarms": [HIGH_PRESSURE_ATTRIBUTES]}
    assert ir.async_get(hass).async_get_issue(DOMAIN, get_alarm_issue_id(entry_id, SENSOR_BREAK_ALARM)) is None
    assert ir.async_get(hass).async_get_issue(DOMAIN, get_alarm_issue_id(entry_id, HIGH_PRESSURE_ALARM)) is not None


@pytest.mark.parametrize(
    ("stored", "alarms", "expected_events"),
    [
        ([], [SENSOR_BREAK_ALARM], [("raised", SENSOR_BREAK_ATTRIBUTES)]),
        ([SENSOR_BREAK_ATTRIBUTES], [], [("cleared", SENSOR_BREAK_ATTRIBUTES)]),
        (
            [SENSOR_BREAK_ATTRIBUTES],
            [HIGH_PRESSURE_ALARM],
            [("cleared", SENSOR_BREAK_ATTRIBUTES), ("raised", HIGH_PRESSURE_ATTRIBUTES)],
        ),
        ([SENSOR_BREAK_ATTRIBUTES], [SENSOR_BREAK_ALARM], []),
        # The same alarm raised again after the restart is a new alarm.
        (
            [{**SENSOR_BREAK_ATTRIBUTES, "timestamp": "2026-10-27T10:00:00+01:00"}],
            [SENSOR_BREAK_ALARM],
            [
                ("cleared", {**SENSOR_BREAK_ATTRIBUTES, "timestamp": "2026-10-27T10:00:00+01:00"}),
                ("raised", SENSOR_BREAK_ATTRIBUTES),
            ],
        ),
    ],
    ids=["raised", "cleared", "cleared_and_raised", "still_pending", "raised_again"],
)
async def test_alarm_events_after_restart(
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
    stored: list[AlarmAttributes],
    alarms: list[AlarmValue],
    expected_events: list[tuple[str, AlarmAttributes]],
) -> None:
    """Test that the alarms raised or cleared while Home Assistant was not running are reported once after the start."""
    key: str = get_alarm_store_key(fake_api.config_entry.entry_id)
    hass_storage[key] = get_alarm_store(key, stored)
    fake_api.responses = get_single_device_responses()
    fake_api.alarms = alarms
    events: list[Event[EventStateChangedData]] = async_capture_events(fake_api.hass, EVENT_STATE_CHANGED)
    await fake_api.setup_integration()

    assert get_alarm_events(events) == expected_events


@pytest.mark.parametrize(
    ("language", "alarms", "expected_requests"),
    [
        ("en", [], ["action=getCount"]),
        ("en", [SENSOR_BREAK_ALARM], ["action=getCount", "action=getAll&languageCode=en"]),
        ("de-CH", [SENSOR_BREAK_ALARM], ["action=getCount", "action=getAll&languageCode=de"]),
    ],
    ids=["without_alarms", "with_alarms", "language_with_region"],
    indirect=["language"],
)
async def test_alarm_requests(
    fake_api: FakeKebaKeEnergyAPI,
    language: str,  # noqa: ARG001
    alarms: list[AlarmValue],
    expected_requests: list[str],
) -> None:
    """Test that the alarms are only read while there are any, in the language of Home Assistant."""
    fake_api.responses = get_single_device_responses()
    fake_api.alarms = alarms
    await fake_api.setup_integration()

    assert fake_api.alarm_requests() == expected_requests


async def test_alarm_invalid_time_zone(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the time of an alarm is in the time zone of Home Assistant if the control unit has an invalid one."""
    fake_api.responses = get_single_device_responses()
    fake_api.timezone = "Invalid/Zone"
    fake_api.alarms = [SENSOR_BREAK_ALARM]
    await fake_api.setup_integration()

    assert get_state(hass, PENDING_ALARMS_ENTITY_ID).attributes[ATTR_ALARMS][0]["time"] == ("2026-10-28T16:53:51-07:00")


@pytest.mark.no_fail_on_keba_errors
async def test_alarm_update_error(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the entities are unavailable if the alarms cannot be read."""
    fake_api.responses = get_single_device_responses(SINGLE_DEVICE_DATA_RESPONSE)
    await fake_api.setup_integration()
    coordinator: KebaKeEnergyDataUpdateCoordinator = fake_api.config_entry.runtime_data.data_coordinator

    fake_api.alarms = HTTPStatus.BAD_REQUEST
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert isinstance(coordinator.last_exception, UpdateFailed)
    assert coordinator.last_exception.translation_key == "communication_error"
    assert get_state(hass, PENDING_ALARMS_ENTITY_ID).state == STATE_UNAVAILABLE
    assert get_state(hass, ALARM_ENTITY_ID).state == STATE_UNAVAILABLE


async def test_unload_entry_deletes_alarm_issues(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that unloading a config entry deletes the repair issues of its alarms."""
    fake_api.responses = get_single_device_responses()
    fake_api.alarms = [SENSOR_BREAK_ALARM]
    await fake_api.setup_integration()

    assert await hass.config_entries.async_unload(fake_api.config_entry.entry_id)
    await hass.async_block_till_done()

    assert (
        ir.async_get(hass).async_get_issue(
            DOMAIN, get_alarm_issue_id(fake_api.config_entry.entry_id, SENSOR_BREAK_ALARM)
        )
        is None
    )


async def test_remove_entry_removes_alarms(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that removing a config entry removes its stored alarms."""
    key: str = get_alarm_store_key(config_entry.entry_id)
    hass_storage[key] = get_alarm_store(key, [SENSOR_BREAK_ATTRIBUTES])
    fake_api.responses = get_single_device_responses()
    fake_api.alarms = [SENSOR_BREAK_ALARM]
    await fake_api.setup_integration()

    await hass.config_entries.async_remove(config_entry.entry_id)
    await hass.async_block_till_done()

    assert key not in hass_storage
