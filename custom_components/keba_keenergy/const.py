"""Constants for the KEBA KeEnergy integration."""

from __future__ import annotations

from typing import Final

ATTR_CONFIG_ENTRY: Final = "config_entry"
ATTR_OFFSET: Final[str] = "offset"
CONFIG_ENTRY_VERSION: Final[int] = 1
DEFAULT_SCAN_INTERVAL = 20
DEFAULT_SSL: Final[bool] = False
DOMAIN: Final[str] = "keba_keenergy"
FLASH_WRITE_LIMIT_PER_WEEK: Final[int] = 30
FLASH_WRITE_DELAY: Final[float] = 1
MANUFACTURER: Final = "KEBA"
MANUFACTURER_MTEC: Final = "M-TEC"
MANUFACTURER_INO: Final = "ino"
MIN_SCAN_INTERVAL = 20
NAME: Final = "KeEnergy"
REQUEST_REFRESH_COOLDOWN: Final[float] = 0.5
SCAN_INTERVAL: Final[int] = 20

SERVICE_SET_AWAY_DATE_RANGE: Final[str] = "set_away_date_range"
SERVICE_SET_HEATING_CURVE_POINTS: Final[str] = "set_heating_curve_points"
