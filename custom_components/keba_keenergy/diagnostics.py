# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Diagnostics support for the KEBA KeEnergy integration."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING
from typing import Any

from homeassistant.components.diagnostics import async_redact_data

from .const import TO_REDACT

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
) -> dict[str, Any]:
    """Return the diagnostics of a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data

    return async_redact_data(
        {
            "entry": {
                "title": entry.title,
                "unique_id": entry.unique_id,
                "data": dict(entry.data),
                "options": dict(entry.options),
            },
            "device": {
                "model": coordinator.device_model,
                "name": coordinator.device_name,
                "hmi_sw_version": coordinator.device_hmi_sw_version,
                "serial_number": coordinator.device_serial_number,
            },
            "position": asdict(coordinator.position) if coordinator.position else None,
            "available_heating_curves": coordinator.available_heating_curves,
            "weekly_write_count": coordinator.weekly_write_count,
            "fixed_data": coordinator.fixed_data,
            "data": coordinator.data,
            "message_ids": coordinator.message_ids,
        },
        TO_REDACT,
    )
