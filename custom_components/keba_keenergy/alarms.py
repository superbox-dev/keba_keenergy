# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Pending alarms of the control unit for the KEBA KeEnergy integration."""

from __future__ import annotations

import logging
from dataclasses import replace
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.storage import Store
from keba_keenergy_api.enums import AlarmPriority
from keba_keenergy_api.models import Alarm

from .const import ALARM_ISSUE_ID
from .const import ALARM_PRIORITY_TO_SEVERITY
from .const import ALARM_TIME_FORMAT
from .const import DOMAIN
from .const import AlarmEventType

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping
    from collections.abc import Sequence
    from datetime import tzinfo

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import CALLBACK_TYPE
    from homeassistant.core import HomeAssistant

_LOGGER: Final = logging.getLogger(__name__)

# An alarm is identified by its component, number, instance and the time it was raised.
type AlarmKey = tuple[int, int, int, datetime]
# The attributes of an alarm event, also the stored alarms.
type AlarmAttributes = dict[str, bool | int | str]
# Called with every raised or cleared alarm.
type AlarmListener = Callable[[AlarmEventType, Alarm], None]


def get_alarm_attributes(alarm: Alarm, /) -> AlarmAttributes:
    """Return the attributes of an alarm, the priority in lowercase and the time in ISO format."""
    return {
        "number": alarm.number,
        "component": alarm.component,
        "instance": alarm.instance,
        "priority": alarm.priority.name.lower(),
        "acknowledgeable": alarm.acknowledgeable,
        "short_text": alarm.short_text,
        "long_text": alarm.long_text,
        "timestamp": alarm.timestamp.isoformat(),
    }


class AlarmMonitor:
    """Report the pending alarms of a control unit as repair issues and as raised and cleared events.

    The reported alarms are stored, so an alarm is not raised again after a restart, and an alarm that was raised or
    cleared while Home Assistant was not running is reported after the start.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, /) -> None:
        """Initialize the alarms of the config entry."""
        self._hass: HomeAssistant = hass
        self._entry: ConfigEntry = entry
        self._store: Store[Mapping[str, Any]] = self._get_store(hass, entry.entry_id)

        # The pending alarms of the last update, with the time zone of the control unit.
        self._alarms: dict[AlarmKey, Alarm] = {}
        self._issue_ids: set[str] = set()
        self._listeners: list[AlarmListener] = []
        # The events of the first update, it runs before the event entity listens.
        self._first_update: bool = True
        self._queued_events: list[tuple[AlarmEventType, Alarm]] = []

    @property
    def pending_alarms(self) -> list[Alarm]:
        """Return the pending alarms, sorted by the time they were raised."""
        return sorted(self._alarms.values(), key=lambda alarm: alarm.timestamp)

    async def async_setup(self) -> None:
        """Load the reported alarms from the store and delete the repair issues when the entry is unloaded."""
        store_data: Mapping[str, Any] = await self._store.async_load() or {}
        alarms: list[Alarm] = [self._from_attributes(attributes) for attributes in store_data.get("alarms", [])]
        self._alarms = {self._get_key(alarm): alarm for alarm in alarms}
        self._entry.async_on_unload(self._delete_issues)

    @staticmethod
    def _from_attributes(attributes: Mapping[str, Any], /) -> Alarm:
        """Return the alarm of its stored attributes."""
        return Alarm(
            number=attributes["number"],
            component=attributes["component"],
            instance=attributes["instance"],
            priority=AlarmPriority[attributes["priority"].upper()],
            acknowledgeable=attributes["acknowledgeable"],
            short_text=attributes["short_text"],
            long_text=attributes["long_text"],
            timestamp=datetime.fromisoformat(attributes["timestamp"]),
        )

    @staticmethod
    def _get_key(alarm: Alarm, /) -> AlarmKey:
        return alarm.component, alarm.number, alarm.instance, alarm.timestamp

    def _delete_issues(self) -> None:
        """Delete the repair issues of all pending alarms."""
        for issue_id in self._issue_ids:
            ir.async_delete_issue(self._hass, domain=DOMAIN, issue_id=issue_id)

        self._issue_ids = set()

    def async_add_listener(self, listener: AlarmListener, /) -> CALLBACK_TYPE:
        """Add a listener of the raised and cleared alarms and return the function that removes it.

        The first listener gets the events of the first update at once.
        """
        self._listeners.append(listener)

        for event_type, alarm in self._queued_events:
            listener(event_type, alarm)

        self._queued_events = []

        def remove_listener() -> None:
            self._listeners.remove(listener)

        return remove_listener

    async def async_update(self, alarms: Sequence[Alarm], /, *, timezone: tzinfo) -> None:
        """Update the repair issues with the pending alarms and report the raised and cleared alarms.

        The time of the alarms is the local time of the control unit in the `timezone`.
        """
        pending_alarms: list[Alarm] = [
            replace(alarm, timestamp=alarm.timestamp.replace(tzinfo=timezone)) for alarm in alarms
        ]
        pending: dict[AlarmKey, Alarm] = {self._get_key(alarm): alarm for alarm in pending_alarms}
        cleared: list[Alarm] = [alarm for key, alarm in self._alarms.items() if key not in pending]
        raised: list[Alarm] = [alarm for key, alarm in pending.items() if key not in self._alarms]

        # The texts of an alarm are replaced as well, e.g. after the language was changed.
        self._alarms = pending
        self._update_issues()

        if raised or cleared:
            _LOGGER.debug(
                "Alarms changed, raised %s, cleared %s",
                [alarm.number for alarm in raised],
                [alarm.number for alarm in cleared],
            )
            await self._store.async_save({"alarms": [get_alarm_attributes(alarm) for alarm in self.pending_alarms]})

        for event_type, changed in ((AlarmEventType.CLEARED, cleared), (AlarmEventType.RAISED, raised)):
            for alarm in sorted(changed, key=lambda alarm: alarm.timestamp):
                self._report(event_type, alarm)

        self._first_update = False

    def _update_issues(self) -> None:
        """Create or update the repair issue of every pending alarm and delete the others."""
        issue_ids: set[str] = set()

        for alarm in self._alarms.values():
            issue_id: str = f"{ALARM_ISSUE_ID}_{self._entry.entry_id}_{alarm.component}_{alarm.number}_{alarm.instance}"
            issue_ids.add(issue_id)

            ir.async_create_issue(
                self._hass,
                domain=DOMAIN,
                issue_id=issue_id,
                is_fixable=False,
                severity=ALARM_PRIORITY_TO_SEVERITY[alarm.priority],
                translation_key=f"{ALARM_ISSUE_ID}_acknowledgeable" if alarm.acknowledgeable else ALARM_ISSUE_ID,
                translation_placeholders={
                    "long_text": alarm.long_text,
                    "name": self._entry.title,
                    "number": str(alarm.number),
                    "short_text": alarm.short_text,
                    "time": alarm.timestamp.strftime(ALARM_TIME_FORMAT),
                },
            )

        for issue_id in self._issue_ids - issue_ids:
            ir.async_delete_issue(self._hass, domain=DOMAIN, issue_id=issue_id)

        self._issue_ids = issue_ids

    def _report(self, event_type: AlarmEventType, alarm: Alarm, /) -> None:
        """Report a raised or cleared alarm to the listeners, kept for the first listener during the first update."""
        if self._first_update and not self._listeners:
            self._queued_events.append((event_type, alarm))

        for listener in self._listeners:
            listener(event_type, alarm)

    @classmethod
    async def async_remove(cls, hass: HomeAssistant, entry_id: str, /) -> None:
        """Remove the stored alarms of a removed config entry."""
        await cls._get_store(hass, entry_id).async_remove()

    @staticmethod
    def _get_store(hass: HomeAssistant, entry_id: str, /) -> Store[Mapping[str, Any]]:
        """Return the store of the reported alarms of a config entry."""
        return Store(hass, version=1, key=f"{DOMAIN}.{entry_id}.alarms")
