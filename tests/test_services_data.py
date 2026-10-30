# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_services.py`."""

from typing import Final

# The away date range from 2025-01-01 to 2025-01-14 in the time zone of the Web HMI.
AWAY_DATE_RANGE_WRITE: Final[str] = (
    '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.start", "value": "1735686000"}, '
    '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.start", "value": "1735686000"}, '
    '{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holiday.stop", "value": "1736895599"}, '
    '{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.holiday.stop", "value": "1736895599"}]'
)

# Nine unsorted points of a heating curve.
HEATING_CURVE_POINTS: Final[list[dict[str, float]]] = [
    {"outdoor": -20, "flow": 35.30},
    {"outdoor": 20, "flow": 23.9},
    {"outdoor": -15, "flow": 33.9},
    {"outdoor": 15, "flow": 25.3},
    {"outdoor": -10, "flow": 32.5},
    {"outdoor": 10, "flow": 26.7},
    {"outdoor": -5, "flow": 31.1},
    {"outdoor": 5, "flow": 28.1},
    {"outdoor": 0, "flow": 29.5},
]

# The `HEATING_CURVE_POINTS` written sorted to the curve HC1, the unused points are 0.
HEATING_CURVE_POINTS_WRITE: Final[str] = (
    '[{"name": "APPL.CtrlAppl.sParam.linTabPool[0].noOfPoints", "value": "9"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[0].x", "value": "-20.0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[0].y", "value": "35.3"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[1].x", "value": "-15.0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[1].y", "value": "33.9"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[2].x", "value": "-10.0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[2].y", "value": "32.5"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[3].x", "value": "-5.0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[3].y", "value": "31.1"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[4].x", "value": "0.0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[4].y", "value": "29.5"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[5].x", "value": "5.0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[5].y", "value": "28.1"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[6].x", "value": "10.0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[6].y", "value": "26.7"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[7].x", "value": "15.0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[7].y", "value": "25.3"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[8].x", "value": "20.0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[8].y", "value": "23.9"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[9].x", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[9].y", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[10].x", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[10].y", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[11].x", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[11].y", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[12].x", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[12].y", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[13].x", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[13].y", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[14].x", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[14].y", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[15].x", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].points[15].y", "value": "0"}, '
    '{"name": "APPL.CtrlAppl.sParam.linTabPool[0].verCnt", "value": "192"}]'
)
