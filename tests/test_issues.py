# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the repair issues."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any

from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.components.water_heater import ATTR_OPERATION_MODE
from homeassistant.components.water_heater import SERVICE_SET_OPERATION_MODE
from homeassistant.components.water_heater.const import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.components.water_heater.const import STATE_PERFORMANCE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import FLASH_WRITE_LIMIT_PER_WEEK
from tests import init_translations
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITION_OTHER_MODES_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from datetime import date

    from homeassistant.core import HomeAssistant

    from tests.conftest import FakeKebaKeEnergyAPI


async def test_issues(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test the repair issue for frequent write operations."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
        # Read the API after the first action call.
        MULTIPLE_POSITION_DATA_RESPONSE,
        # Read the API after the first action call.
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    today: date = dt_util.now().date()
    hass_storage[DOMAIN] = {
        "version": 1,
        "minor_version": 1,
        "key": DOMAIN,
        "data": {
            "flash_write_counter": {
                "week": [today.isocalendar().year, today.isocalendar().week],
                "count": FLASH_WRITE_LIMIT_PER_WEEK,
            },
        },
    }
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="issues")

    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: "select.keba_keenergy_12345678_buffer_tank_operating_mode_1",
            ATTR_OPTION: "on",
        },
        blocking=True,
    )

    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: "select.keba_keenergy_12345678_buffer_tank_operating_mode_1",
            ATTR_OPTION: "off",
        },
        blocking=True,
    )

    issue_registry: ir.IssueRegistry = ir.async_get(hass)

    issue: ir.IssueEntry | None = issue_registry.async_get_issue(
        DOMAIN,
        "frequent_flash_writes",
    )

    assert issue is not None
    assert issue.severity == ir.IssueSeverity.WARNING

    title: str = translations[f"component.keba_keenergy.issues.{issue.translation_key}.title"]
    description: str = translations[f"component.keba_keenergy.issues.{issue.translation_key}.description"].format(
        **(issue.translation_placeholders or {}),
    )

    assert title == "Frequent write operations detected"
    assert description == (
        "More than 30 write operations were performed on the device this week.\n\n"
        "Very frequent write operations (for example caused by automations) may reduce the lifetime of the device's "
        "flash memory."
    )


async def test_issues_translated(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test the German translation of the repair issue for frequent write operations."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
        # Read the API after the first action call.
        MULTIPLE_POSITION_DATA_RESPONSE,
        # Read the API after the second action call.
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    today: date = dt_util.now().date()
    hass_storage[DOMAIN] = {
        "version": 1,
        "minor_version": 1,
        "key": DOMAIN,
        "data": {
            "flash_write_counter": {
                "week": [today.isocalendar().year, today.isocalendar().week],
                "count": FLASH_WRITE_LIMIT_PER_WEEK,
            },
        },
    }
    hass.config.language = "de"
    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="issues")

    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: "select.keba_keenergy_12345678_buffer_tank_operating_mode_1",
            ATTR_OPTION: "on",
        },
        blocking=True,
    )

    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: "select.keba_keenergy_12345678_buffer_tank_operating_mode_1",
            ATTR_OPTION: "off",
        },
        blocking=True,
    )

    issue_registry: ir.IssueRegistry = ir.async_get(hass)

    issue: ir.IssueEntry | None = issue_registry.async_get_issue(
        DOMAIN,
        "frequent_flash_writes",
    )

    assert issue is not None
    assert issue.severity == ir.IssueSeverity.WARNING

    title: str = translations[f"component.keba_keenergy.issues.{issue.translation_key}.title"]
    description: str = translations[f"component.keba_keenergy.issues.{issue.translation_key}.description"].format(
        **(issue.translation_placeholders or {}),
    )

    assert title == "Viele Schreibzugriffe erkannt"
    assert description == (
        "In dieser Woche wurden mehr als 30 Schreibzugriffe auf das Gerät durchgeführt.\n\n"
        "Sehr häufige Schreibzugriffe (zum Beispiel durch Automationen) können die Lebensdauer des "
        "Flash-Speichers des Geräts reduzieren."
    )


async def test_ignored_write_is_not_counted(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that a write that is not counted (heat up the hot water tank) keeps the weekly write counter."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_OTHER_MODES_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_POSITION_OTHER_MODES_DATA_RESPONSE,
    ]
    today: date = dt_util.now().date()
    week: list[int] = [today.isocalendar().year, today.isocalendar().week]
    hass_storage[DOMAIN] = {
        "version": 1,
        "minor_version": 1,
        "key": DOMAIN,
        "data": {
            "flash_write_counter": {
                "week": week,
                "count": 5,
            },
        },
    }
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=WATER_HEATER_DOMAIN,
        service=SERVICE_SET_OPERATION_MODE,
        service_data={
            ATTR_ENTITY_ID: "water_heater.keba_keenergy_12345678_1",
            ATTR_OPERATION_MODE: STATE_PERFORMANCE,
        },
        blocking=True,
    )

    assert len(fake_api.write_requests()) == 1
    assert hass_storage[DOMAIN]["data"]["flash_write_counter"] == {"week": week, "count": 5}


async def test_new_week_resets_write_counter(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    hass_storage: dict[str, Any],
) -> None:
    """Test that the first write of a new week resets the write counter and removes the repair issue."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
        # Read the API after the action call.
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    today: date = dt_util.now().date()
    last_week: date = today - timedelta(weeks=1)
    hass_storage[DOMAIN] = {
        "version": 1,
        "minor_version": 1,
        "key": DOMAIN,
        "data": {
            "flash_write_counter": {
                "week": [last_week.isocalendar().year, last_week.isocalendar().week],
                "count": FLASH_WRITE_LIMIT_PER_WEEK + 1,
            },
        },
    }
    ir.async_create_issue(
        hass,
        domain=DOMAIN,
        issue_id="frequent_flash_writes",
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key="frequent_flash_writes",
    )
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: "select.keba_keenergy_12345678_buffer_tank_operating_mode_1",
            ATTR_OPTION: "on",
        },
        blocking=True,
    )

    assert ir.async_get(hass).async_get_issue(DOMAIN, "frequent_flash_writes") is None
    assert hass_storage[DOMAIN]["data"]["flash_write_counter"] == {
        "week": [today.isocalendar().year, today.isocalendar().week],
        "count": 1,
    }
