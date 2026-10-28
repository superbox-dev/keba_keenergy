# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Test data for `test_binary_sensor.py`."""

from typing import Final

COMPRESSOR_FAILURE_ENTITY_ID: Final[str] = "binary_sensor.keba_keenergy_12345678_heat_pump_has_compressor_failure"
COMPRESSOR_FAILURE_MESSAGE_ID: Final[str] = "APPL.CtrlAppl.sParam.heatpump[0].FailureCompressor.state.msgId"
