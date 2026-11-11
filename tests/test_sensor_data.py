# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_sensor.py`."""

from typing import Final

from tests import replace_values
from tests.const import CURVE_NAMES_RESPONSE
from tests.const import CURVE_POINTS_RESPONSE
from tests.const import Response

# The control unit has no curves, so the curves in use (e.g. `HC6`) do not exist.
CURVES_WITHOUT_NAMES_RESPONSE: Final[list[Response]] = [
    replace_values(CURVE_NAMES_RESPONSE, dict.fromkeys((value["name"] for value in CURVE_NAMES_RESPONSE), "")),
    CURVE_POINTS_RESPONSE,
]
