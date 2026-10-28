# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_translations.py`."""

from pathlib import Path
from typing import Final

import custom_components.keba_keenergy

INTEGRATION_DIR: Final[Path] = Path(custom_components.keba_keenergy.__file__).parent
STRINGS: Final[Path] = INTEGRATION_DIR / "strings.json"
TRANSLATIONS: Final[list[Path]] = sorted((INTEGRATION_DIR / "translations").glob("*.json"))
