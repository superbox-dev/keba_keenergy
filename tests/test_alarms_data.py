# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Constants for the tests of the alarms."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Final

from custom_components.keba_keenergy.const import ALARM_ISSUE_ID
from custom_components.keba_keenergy.const import DOMAIN

if TYPE_CHECKING:
    from tests.api_data import AlarmValue

# The attributes of an alarm event, also the stored alarms.
type AlarmAttributes = dict[str, bool | int | str]

ALARM_ENTITY_ID: Final = "event.keba_keenergy_12345678_alarm"
PENDING_ALARMS_ENTITY_ID: Final = "sensor.keba_keenergy_12345678_pending_alarms"

# The `SENSOR_BREAK_ALARM` with the time zone of the control unit (`Europe/Vienna`).
SENSOR_BREAK_ATTRIBUTES: Final[AlarmAttributes] = {
    "number": 700,
    "component": 100,
    "instance": 1,
    "priority": "error",
    "acknowledgeable": False,
    "short_text": "Sensor source temperature",
    "long_text": "Differential control 1 Diff. Regler 1: Sensor source temperature broken (53 - Sensor break)",
    "timestamp": "2026-10-28T16:53:51+01:00",
}

# The `HIGH_PRESSURE_ALARM` with the time zone of the control unit (`Europe/Vienna`).
HIGH_PRESSURE_ATTRIBUTES: Final[AlarmAttributes] = {
    "number": 12,
    "component": 200,
    "instance": 2,
    "priority": "emergency",
    "acknowledgeable": True,
    "short_text": "High pressure switch",
    "long_text": "Heat pump 2 Wärmepumpe 2: High pressure switch tripped",
    "timestamp": "2026-10-29T07:05:00+01:00",
}

# The pending alarms of the sensor for the `SENSOR_BREAK_ALARM` and the `HIGH_PRESSURE_ALARM`.
PENDING_ALARMS: Final[list[dict[str, int | str]]] = [
    {
        "number": 700,
        "text": "Differential control 1 Diff. Regler 1: Sensor source temperature broken (53 - Sensor break)",
        "priority": "error",
        "time": "2026-10-28T16:53:51+01:00",
    },
    {
        "number": 12,
        "text": "Heat pump 2 Wärmepumpe 2: High pressure switch tripped",
        "priority": "emergency",
        "time": "2026-10-29T07:05:00+01:00",
    },
]


def get_alarm_issue_id(entry_id: str, alarm: AlarmValue, /) -> str:
    """Return the ID of the repair issue of an alarm of the config entry."""
    return f"{ALARM_ISSUE_ID}_{entry_id}_{alarm['compNr']}_{alarm['alarmNr']}_{alarm['instanceNr']}"


def get_alarm_store_key(entry_id: str, /) -> str:
    """Return the key of the stored alarms of the config entry."""
    return f"{DOMAIN}.{entry_id}.alarms"


def get_alarm_store(key: str, alarms: list[AlarmAttributes], /) -> dict[str, Any]:
    """Return the stored data of the reported alarms with the key."""
    return {
        "version": 1,
        "minor_version": 1,
        "key": key,
        "data": {"alarms": alarms},
    }
