"""Support for the KEBA KeEnergy services."""

import logging
from datetime import date
from datetime import datetime
from datetime import time
from typing import Final
from typing import TYPE_CHECKING

import voluptuous as vol
from ciso8601 import parse_datetime_as_naive
from homeassistant.config_entries import ConfigEntry
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.core import ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from keba_keenergy_api.constants import HeatCircuitHeatingCurve
from keba_keenergy_api.constants import MAX_HEATING_CURVE_POINTS
from keba_keenergy_api.endpoints import HeatingCurvePoint
from keba_keenergy_api.endpoints import HeatingCurvePoints
from keba_keenergy_api.endpoints import HeatingCurves

from .const import ATTR_CONFIG_ENTRY
from .const import DOMAIN
from .const import SERVICE_SET_AWAY_DATE_RANGE
from .const import SERVICE_SET_HEATING_CURVE_POINTS
from .coordinator import KebaKeEnergyDataUpdateCoordinator

if TYPE_CHECKING:
    from zoneinfo import ZoneInfo

_LOGGER = logging.getLogger(__name__)

ATTR_START_DATE: Final[str] = "start_date"
ATTR_END_DATE: Final[str] = "end_date"

AWAY_DATE_RANGE_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY): selector.ConfigEntrySelector(
            {
                "integration": DOMAIN,
            },
        ),
        vol.Required(ATTR_START_DATE): cv.string,
        vol.Required(ATTR_END_DATE): cv.string,
    },
)

ATTR_POINTS: Final[str] = "points"
ATTR_OUTDOOR: Final[str] = "outdoor"
ATTR_FLOW: Final[str] = "flow"
ATTR_HEATING_CURVE: Final[str] = "heating_curve"

HEATING_CURVE_POINT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_OUTDOOR): vol.All(
            vol.Coerce(float),
            vol.Range(min=-40, max=40),
        ),
        vol.Required(ATTR_FLOW): vol.All(
            vol.Coerce(float),
            vol.Range(min=10, max=90),
        ),
    },
)

HEATING_CURVE_POINTS_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY): selector.ConfigEntrySelector(
            {
                "integration": DOMAIN,
            },
        ),
        vol.Required(ATTR_HEATING_CURVE): vol.In([_.name for _ in HeatCircuitHeatingCurve]),
        vol.Required(ATTR_POINTS): vol.All(
            cv.ensure_list,
            vol.Length(max=MAX_HEATING_CURVE_POINTS),
            [HEATING_CURVE_POINT_SCHEMA],
        ),
    },
)


def __get_coordinator(call: ServiceCall) -> KebaKeEnergyDataUpdateCoordinator:
    """Get the coordinator from the entry."""
    entry_id: str = call.data[ATTR_CONFIG_ENTRY]
    entry: ConfigEntry | None = call.hass.config_entries.async_get_entry(entry_id)

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

    coordinator: KebaKeEnergyDataUpdateCoordinator = call.hass.data[DOMAIN][entry_id]

    return coordinator


async def _async_set_away_range(call: ServiceCall) -> None:
    coordinator: KebaKeEnergyDataUpdateCoordinator = __get_coordinator(call)

    start_date: str | None = call.data.get(ATTR_START_DATE)
    end_date: str | None = call.data.get(ATTR_END_DATE)

    if start_date and end_date:
        tz: ZoneInfo = await coordinator.get_timezone()

        start_date_naive: date = parse_datetime_as_naive(start_date).date()
        end_date_naive: date = parse_datetime_as_naive(end_date).date()

        start_date_tz = datetime.combine(start_date_naive, time.min, tzinfo=tz)
        end_date_tz = datetime.combine(end_date_naive, time.max, tzinfo=tz)

        if end_date_tz < start_date_tz:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="end_date_smaller_than_start_date",
            )

        await coordinator.set_away_date_range(
            start_timestamp=start_date_tz.timestamp(),
            end_timestamp=end_date_tz.timestamp(),
        )


async def _async_set_heating_curve_points(call: ServiceCall) -> None:
    coordinator: KebaKeEnergyDataUpdateCoordinator = __get_coordinator(call)

    heating_curve: str = call.data[ATTR_HEATING_CURVE]
    heating_curves: HeatingCurves = await coordinator.api.heat_circuit.get_heating_curve_points()

    if not heating_curves.get(heating_curve.lower()):
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="cannot_find_heating_curve",
            translation_placeholders={
                "heating_curve": heating_curve.upper(),
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

    await coordinator.async_execute_write(
        write_fn=lambda: coordinator.api.heat_circuit.set_heating_curve_points(
            heating_curve=heating_curve,
            points=points,
        ),
    )


async def async_setup_services(hass: HomeAssistant) -> None:
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
