# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Support for the KEBA KeEnergy services."""

from __future__ import annotations

import logging
from datetime import date
from datetime import datetime
from datetime import time
from typing import TYPE_CHECKING
from typing import Final

import probatio
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from keba_keenergy_api.endpoints import HeatingCurvePoint
from keba_keenergy_api.endpoints import HeatingCurvePoints
from keba_keenergy_api.endpoints import HeatingCurves

from .const import ATTR_CONFIG_ENTRY
from .const import ATTR_END_DATE
from .const import ATTR_FLOW
from .const import ATTR_HEATING_CURVE
from .const import ATTR_OUTDOOR
from .const import ATTR_POINTS
from .const import ATTR_START_DATE
from .const import DOMAIN
from .const import HEATING_CURVE_POINTS_SCHEMA
from .const import SERVICE_SET_AWAY_DATE_RANGE
from .const import SERVICE_SET_HEATING_CURVE_POINTS

if TYPE_CHECKING:
    from zoneinfo import ZoneInfo

    from homeassistant.core import HomeAssistant
    from homeassistant.core import ServiceCall

    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator

_LOGGER: Final = logging.getLogger(__name__)


def _date(value: object) -> date:
    """Validate a date, a date with time (as before) only uses the date."""
    try:
        return cv.date(value)
    except probatio.Invalid:
        return cv.datetime(value).date()


AWAY_DATE_RANGE_SCHEMA: Final[probatio.Schema] = probatio.Schema(
    {
        probatio.Required(ATTR_CONFIG_ENTRY): selector.ConfigEntrySelector(
            {
                "integration": DOMAIN,
            },
        ),
        probatio.Required(ATTR_START_DATE): _date,
        probatio.Required(ATTR_END_DATE): _date,
    },
)


def _get_coordinator(call: ServiceCall) -> KebaKeEnergyDataUpdateCoordinator:
    """Get the coordinator from the entry."""
    entry_id: str = call.data[ATTR_CONFIG_ENTRY]
    entry: KebaKeEnergyConfigEntry | None = call.hass.config_entries.async_get_entry(entry_id)

    if not entry:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="invalid_config_entry",
            translation_placeholders={
                "config_entry_id": entry_id,
            },
        )

    if entry.state != ConfigEntryState.LOADED:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="unloaded_config_entry",
            translation_placeholders={
                "config_entry_id": entry.title,
            },
        )

    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data

    return coordinator


async def _async_set_away_range(call: ServiceCall) -> None:
    coordinator: KebaKeEnergyDataUpdateCoordinator = _get_coordinator(call)

    start_date: date = call.data[ATTR_START_DATE]
    end_date: date = call.data[ATTR_END_DATE]

    if end_date < start_date:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="end_date_smaller_than_start_date",
        )

    tz: ZoneInfo = await coordinator.get_timezone()

    start_date_tz: datetime = datetime.combine(start_date, time.min, tzinfo=tz)
    end_date_tz: datetime = datetime.combine(end_date, time.max, tzinfo=tz)

    await coordinator.set_away_date_range(
        start_timestamp=start_date_tz.timestamp(),
        end_timestamp=end_date_tz.timestamp(),
    )


async def _async_set_heating_curve_points(call: ServiceCall) -> None:
    coordinator: KebaKeEnergyDataUpdateCoordinator = _get_coordinator(call)

    heating_curve: str = call.data[ATTR_HEATING_CURVE]
    heating_curves: HeatingCurves = await coordinator.get_heating_curve_points()

    if heating_curve not in heating_curves:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="cannot_find_heating_curve",
            translation_placeholders={
                "heating_curve": heating_curve,
            },
        )

    points: HeatingCurvePoints = tuple(
        HeatingCurvePoint(
            outdoor=round(d[ATTR_OUTDOOR], 2),
            flow=round(d[ATTR_FLOW], 2),
        )
        for d in sorted(call.data[ATTR_POINTS], key=lambda p: p[ATTR_OUTDOOR])
    )
    outdoors: list[float] = [p.outdoor for p in points]

    if len(outdoors) != len(set(outdoors)):
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="duplicate_outdoor_temperature_values",
        )

    # Only write changed points, the control unit stores them in its flash memory.
    current_points: HeatingCurvePoints = tuple(
        HeatingCurvePoint(outdoor=round(p.outdoor, 2), flow=round(p.flow, 2)) for p in heating_curves[heating_curve]
    )

    if current_points == points:
        return

    await coordinator.async_execute_write(
        write_fn=lambda: coordinator.api.heat_circuit.set_heating_curve_points(
            heating_curve=heating_curve,
            points=points,
        ),
    )


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """KEBA KeEnergy services setup."""
    hass.services.async_register(
        DOMAIN,
        service=SERVICE_SET_AWAY_DATE_RANGE,
        service_func=_async_set_away_range,
        schema=AWAY_DATE_RANGE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        service=SERVICE_SET_HEATING_CURVE_POINTS,
        service_func=_async_set_heating_curve_points,
        schema=HEATING_CURVE_POINTS_SCHEMA,
    )
