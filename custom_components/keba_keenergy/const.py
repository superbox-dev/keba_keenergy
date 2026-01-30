"""Constants for the KEBA KeEnergy integration."""

from typing import Final

ATTR_CONFIG_ENTRY: Final = "config_entry"
ATTR_OFFSET: Final[str] = "offset"
CONFIG_ENTRY_VERSION: Final[int] = 1
DEFAULT_SSL: Final[bool] = False
DOMAIN: Final[str] = "keba_keenergy"
FLASH_WRITE_LIMIT_PER_WEEK: Final[int] = 15
FLASH_WRITE_DELAY: Final[float] = 0.5
MANUFACTURER: Final = "KEBA"
MANUFACTURER_MTEC: Final = "M-TEC"
MANUFACTURER_INO: Final = "ino"
NAME: Final = "KeEnergy"
REQUEST_REFRESH_COOLDOWN: Final[float] = 0.5
SCAN_INTERVAL: Final[int] = 20

SERVICE_SET_AWAY_DATE_RANGE: Final[str] = "set_away_date_range"
