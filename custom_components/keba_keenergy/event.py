# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Support for the KEBA KeEnergy events."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final

from homeassistant.components.event import DOMAIN as EVENT_DOMAIN
from homeassistant.components.event import EventEntity
from homeassistant.components.event import EventEntityDescription

from .alarms import get_alarm_attributes
from .const import AlarmEventType
from .const import SectionPrefix
from .entity import KebaKeEnergyBaseEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from keba_keenergy_api.models import Alarm

    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator

PARALLEL_UPDATES: Final[int] = 0


class KebaKeEnergyAlarmEventEntity(KebaKeEnergyBaseEntity, EventEntity):
    """KEBA KeEnergy event of the raised and cleared alarms of the control unit."""

    _platform_domain: str = EVENT_DOMAIN

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: EventEntityDescription,
        /,
    ) -> None:
        """Initialize the alarm event of the control unit."""
        self.entity_description: EventEntityDescription = description

        super().__init__(coordinator, device_type=SectionPrefix.SYSTEM, index=None)

    @property
    def _unique_id_parts(self) -> tuple[str, ...]:
        """Return the key of the entity description."""
        return (self.entity_description.key,)

    async def async_added_to_hass(self) -> None:
        """Listen to the raised and cleared alarms after the first state of the entity is written.

        The alarms of the first update are reported then, the triggers of Home Assistant ignore the first state.
        """
        await super().async_added_to_hass()
        # Not started eagerly, so the task runs after the first state is written.
        self.coordinator.config_entry.async_create_task(
            self.hass,
            self._async_add_alarm_listener(),
            f"{self.entity_id} alarm listener",
            eager_start=False,
        )

    async def _async_add_alarm_listener(self) -> None:
        """Add the listener of the alarms, the first listener gets the alarms of the first update at once."""
        self.async_on_remove(self.coordinator.alarms.async_add_listener(self._handle_alarm))

    def _handle_alarm(self, event_type: AlarmEventType, alarm: Alarm, /) -> None:
        """Trigger the event of a raised or cleared alarm."""
        self._trigger_event(event_type, get_alarm_attributes(alarm))
        self.async_write_ha_state()


ALARM_EVENT_TYPE: Final[EventEntityDescription] = EventEntityDescription(
    event_types=[event_type.value for event_type in AlarmEventType],
    key="alarm",
    translation_key="alarm",
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy events from a config entry."""
    async_add_entities([KebaKeEnergyAlarmEventEntity(entry.runtime_data.data_coordinator, ALARM_EVENT_TYPE)])
