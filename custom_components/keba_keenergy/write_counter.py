# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Weekly counter of the flash write operations for the KEBA KeEnergy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.storage import Store
from homeassistant.util.dt import now

from .const import DOMAIN
from .const import FLASH_WRITE_ISSUE_ID
from .const import FLASH_WRITE_LIMIT_PER_WEEK

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping
    from datetime import date
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


class FlashWriteCounter:
    """Count the write operations of a control unit per week and warn with a repair issue above the limit."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, /, *, on_change: Callable[[], None]) -> None:
        """Initialize the write counter of the config entry, `on_change` is called after every change."""
        self._hass: HomeAssistant = hass
        self._entry: ConfigEntry = entry
        self._on_change: Callable[[], None] = on_change
        self._store: Store[Mapping[str, Any]] = self._get_store(hass, entry_id=entry.entry_id)

        self._weekly_count: int = 0
        self._weekly_writes: dict[str, int] = {}
        self._week: tuple[int, int] | None = None

    @property
    def weekly_count(self) -> int:
        """Return the number of writes in the current week."""
        return self._weekly_count

    @property
    def weekly_writes(self) -> dict[str, int]:
        """Return how often each value was written in the current week, sorted by name."""
        return dict(sorted(self._weekly_writes.items()))

    @property
    def _issue_id(self) -> str:
        """Return the ID of the repair issue for frequent write operations of this control unit."""
        return f"{FLASH_WRITE_ISSUE_ID}_{self._entry.entry_id}"

    async def async_setup(self) -> None:
        """Load the counter from the store and reset it at midnight of every new week, until the entry is unloaded."""
        store_data: Mapping[str, Any] = await self._store.async_load() or {}
        counter: dict[str, Any] | None = store_data.get("flash_write_counter")

        if isinstance(counter, dict):
            # An unknown week is stored as an empty list.
            week: list[int] = counter["week"]
            self._week = (week[0], week[1]) if week else None
            self._weekly_count = counter["count"]
            self._weekly_writes = counter.get("writes", {})

        # A counter of a past week is reset here, e.g. if Home Assistant was not running at midnight.
        await self._async_reset_if_new_week()
        # Home Assistant does not restore the repair issue after a restart, because it is not persistent.
        self._create_issue_if_over_limit()
        self._entry.async_on_unload(
            async_track_time_change(self._hass, self._async_reset_if_new_week, hour=0, minute=0, second=0),
        )

        # Older versions stored one counter and created one repair issue for all config entries.
        # TODO: Remove this cleanup and the shared store once hardly any installation updates from those versions.
        await self._get_store(self._hass).async_remove()
        ir.async_delete_issue(self._hass, domain=DOMAIN, issue_id=FLASH_WRITE_ISSUE_ID)

    async def _async_reset_if_new_week(self, _now: datetime | None = None, /) -> None:
        """Reset and save the counter in a new week, `_now` is the time of the timer at midnight."""
        if self._reset_if_new_week():
            await self._async_save()
            self._on_change()

    def _reset_if_new_week(self) -> bool:
        """Reset the counter in a new week without saving it, return True if it was reset."""
        today: date = now().date()
        current_week: tuple[int, int] = today.isocalendar().year, today.isocalendar().week

        if self._week == current_week:
            return False

        self._week = current_week
        self._weekly_count = 0
        self._weekly_writes = {}

        ir.async_delete_issue(
            self._hass,
            domain=DOMAIN,
            issue_id=self._issue_id,
        )

        return True

    async def _async_save(self) -> None:
        await self._store.async_save(
            {
                "flash_write_counter": {
                    "week": list(self._week) if self._week else [],
                    "count": self._weekly_count,
                    "writes": self._weekly_writes,
                },
            },
        )

    async def async_add_write(self, names: tuple[str, ...], /) -> None:
        """Count a write of the values with the names.

        The names are counted separately, a write of several values counts once in total.
        """
        self._reset_if_new_week()
        self._weekly_count += 1

        for name in names:
            self._weekly_writes[name] = self._weekly_writes.get(name, 0) + 1

        await self._async_save()
        self._on_change()

        self._create_issue_if_over_limit()

    def _create_issue_if_over_limit(self) -> None:
        """Create the repair issue if the counter exceeds the limit, an existing issue is kept."""
        if self._weekly_count <= FLASH_WRITE_LIMIT_PER_WEEK:
            return

        ir.async_create_issue(
            self._hass,
            domain=DOMAIN,
            issue_id=self._issue_id,
            is_fixable=False,
            translation_key=FLASH_WRITE_ISSUE_ID,
            translation_placeholders={
                "limit": str(FLASH_WRITE_LIMIT_PER_WEEK),
                "name": self._entry.title,
            },
            severity=ir.IssueSeverity.WARNING,
        )

    @classmethod
    async def async_remove(cls, hass: HomeAssistant, entry_id: str, /) -> None:
        """Remove the stored counter of a removed config entry."""
        await cls._get_store(hass, entry_id=entry_id).async_remove()

    @staticmethod
    def _get_store(hass: HomeAssistant, /, *, entry_id: str | None = None) -> Store[Mapping[str, Any]]:
        """Return the store of the counter of a config entry, without entry ID the store shared by all entries.

        The shared store was used by older versions and is only removed.
        """
        return Store(hass, version=1, key=DOMAIN if entry_id is None else f"{DOMAIN}.{entry_id}")
