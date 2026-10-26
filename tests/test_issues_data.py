# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Constants for the tests of the write counter and the repair issues."""

from __future__ import annotations

from typing import Final

ISSUE_DESCRIPTION_DE: Final[str] = (
    "In dieser Woche wurden mehr als 30 Schreibzugriffe auf KEBA KeEnergy (ap4400.local) durchgeführt.\n\n"
    "Sehr häufige Schreibzugriffe (zum Beispiel durch Automationen) können die Lebensdauer des Flash-Speichers des "
    "Geräts reduzieren. Der Sensor „Schreibzugriffe diese Woche“ zeigt, welche Werte wie oft geschrieben wurden."
)
ISSUE_DESCRIPTION_EN: Final[str] = (
    "More than 30 write operations were performed on KEBA KeEnergy (ap4400.local) this week.\n\n"
    "Very frequent write operations (for example caused by automations) may reduce the lifetime of the device's "
    'flash memory. The sensor "Write operations this week" shows which values were written how often.'
)
WRITE_COUNT_ENTITY_ID: Final[str] = "sensor.keba_keenergy_12345678_weekly_write_count"
WRITES_PER_VALUE: Final[dict[str, int]] = {
    "buffer_tank_2.operating_mode": 1,
    "heat_circuit_1.away_end_date": 1,
    "heat_circuit_1.away_start_date": 1,
    "heat_circuit_2.away_end_date": 1,
    "heat_circuit_2.away_start_date": 1,
    "heating_curve_points.HC1": 1,
    "solar_circuit_2.target_temperature_1": 1,
    "system.operating_mode": 1,
}
