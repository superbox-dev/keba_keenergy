# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Diagnostics support for the KEBA KeEnergy integration."""

from __future__ import annotations

from dataclasses import asdict
from enum import Enum
from typing import TYPE_CHECKING
from typing import Any

from homeassistant.components.diagnostics import async_redact_data

from .const import TO_REDACT

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .coordinator import CoordinatorData
    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator
    from .coordinator import KebaKeEnergyRemoteAccessCoordinator

# The readings per device type and key as JSON data.
type ReadingsDump = dict[str, dict[str, list[dict[str, Any]]]]


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
) -> dict[str, Any]:
    """Return the diagnostics of a config entry."""
    data_coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data.data_coordinator
    remote_access_coordinator: KebaKeEnergyRemoteAccessCoordinator = entry.runtime_data.remote_access_coordinator

    return async_redact_data(
        {
            "entry": {
                "title": entry.title,
                "unique_id": entry.unique_id,
                "data": dict(entry.data),
                "options": dict(entry.options),
            },
            "device": {
                "model": data_coordinator.device_model,
                "name": data_coordinator.device_name,
                "hmi_sw_version": data_coordinator.device_hmi_sw_version,
                "serial_number": data_coordinator.device_serial_number,
            },
            "device_counts": asdict(data_coordinator.device_counts) if data_coordinator.device_counts else None,
            "curve_names": data_coordinator.curve_names,
            "weekly_write_count": data_coordinator.write_counter.weekly_count,
            "weekly_writes": data_coordinator.write_counter.weekly_writes,
            "configuration": _dump(data_coordinator.configuration),
            "data": _dump(data_coordinator.data),
            "remote_access": remote_access_coordinator.data,
        },
        TO_REDACT,
    )


def _dump(data: CoordinatorData, /) -> ReadingsDump:
    """Return the readings as JSON data, enum members by their name."""
    return {
        device_type: {
            key: [
                {
                    **asdict(reading),
                    "value": reading.value.name if isinstance(reading.value, Enum) else reading.value,
                    "message_id": None if reading.message_id is None else reading.message_id.value,
                }
                for reading in readings
            ]
            for key, readings in readings_by_key.items()
        }
        for device_type, readings_by_key in data.items()
    }
