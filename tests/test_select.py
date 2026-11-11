# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the select entities."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
from homeassistant.components.select import ATTR_OPTIONS
from homeassistant.const import STATE_UNKNOWN
from homeassistant.const import Platform
from homeassistant.exceptions import ServiceValidationError
from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from pytest_homeassistant.common import snapshot_platform

from tests import copy_values
from tests import get_option_translations
from tests import get_platform_states
from tests import get_state
from tests import next_update
from tests import replace_values
from tests import select_option
from tests.const import CURVE_RENAMED_VALUES
from tests.const import NOW
from tests.const import PASSIVE_COOLING_VALUES
from tests.test_select_data import CURVE_SELECTS
from tests.test_select_data import HEATING_CURVE_ENTITY_ID
from tests.test_select_data import SECOND_HEAT_PUMP_PASSIVE_COOLING_VALUES
from tests.test_select_data import TWO_HEAT_PUMPS_VALUES
from tests.test_select_data import WITHOUT_COOLING_VALUES

if TYPE_CHECKING:
    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
    from homeassistant.helpers import entity_registry as er
    from pytest_homeassistant.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI
    from tests.const import Response

pytestmark = pytest.mark.freeze_time(NOW)


@pytest.mark.parametrize("language", ["de", "en"], ids=["de", "en"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_selects(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    language: str,
) -> None:
    """Test the states and the translated options of all select entities, with cooling."""
    hass.config.language = language
    fake_api.load_device("multiple_devices")
    fake_api.platforms = [Platform.SELECT]
    fake_api.fixed_data = replace_values(fake_api.fixed_data, PASSIVE_COOLING_VALUES)
    await fake_api.setup_integration()

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)

    states: list[State] = get_platform_states(hass, entity_registry, mock_config_entry, Platform.SELECT)
    translated_states: list[State] = [state for state in states if state.entity_id not in CURVE_SELECTS]

    for state in translated_states:
        assert await get_option_translations(hass, entity_registry, state) == snapshot(
            name=f"{state.entity_id}_options"
        )


@pytest.mark.parametrize(
    "entity_id",
    [
        "select.keba_keenergy_12345678_operating_mode",
        "select.keba_keenergy_12345678_heat_circuit_operating_mode_1",
        "select.keba_keenergy_12345678_heat_circuit_operating_mode_2",
    ],
    ids=["operating_mode", "heat_circuit_operating_mode_1", "heat_circuit_operating_mode_2"],
)
@pytest.mark.parametrize("language", ["de", "en"], ids=["de", "en"])
async def test_selects_without_cooling(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    entity_id: str,
    language: str,
) -> None:
    """Test the operating mode selects of a setup without cooling."""
    hass.config.language = language
    fake_api.load_device("multiple_devices")
    fake_api.fixed_data = replace_values(fake_api.fixed_data, WITHOUT_COOLING_VALUES)
    await fake_api.setup_integration()

    state: State = get_state(hass, entity_id)
    assert state == snapshot(name=entity_id)
    assert await get_option_translations(hass, entity_registry, state) == snapshot(name=f"{entity_id}_options")


async def test_system_operating_mode_cooling_of_second_heat_pump(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the system operating mode offers the cooling modes if only the second heat pump can cool."""
    fake_api.load_device("multiple_devices")
    fixed_data: Response = replace_values(fake_api.fixed_data, WITHOUT_COOLING_VALUES)
    fake_api.device_numbers = replace_values(fake_api.device_numbers, TWO_HEAT_PUMPS_VALUES)
    # The second heat pump has the values of the first one.
    fake_api.fixed_data = [
        *fixed_data,
        *replace_values(
            copy_values(fixed_data, ".heatpump[0]", ".heatpump[1]"),
            SECOND_HEAT_PUMP_PASSIVE_COOLING_VALUES,
        ),
    ]
    fake_api.data = [*fake_api.data, *copy_values(fake_api.data, ".heatpump[0]", ".heatpump[1]")]
    await fake_api.setup_integration()

    state: State = get_state(hass, "select.keba_keenergy_12345678_operating_mode")
    assert "auto_cool" in state.attributes[ATTR_OPTIONS]


@pytest.mark.parametrize(
    ("entity_id", "option", "expected"),
    [
        (
            "select.keba_keenergy_12345678_operating_mode",
            "auto_cool",
            '[{"name": "APPL.CtrlAppl.sParam.param.operatingMode", "value": "3"}]',
        ),
        (
            "select.keba_keenergy_12345678_heat_circuit_operating_mode_1",
            "off",
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode", "value": "0"}]',
        ),
        (
            "select.keba_keenergy_12345678_solar_circuit_operating_mode_1",
            "on",
            '[{"name": "APPL.CtrlAppl.sParam.solarCircuit[0].param.operatingMode", "value": "1"}]',
        ),
        (
            "select.keba_keenergy_12345678_hot_water_tank_operating_mode_2",
            "heat_up",
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[1].param.operatingMode", "value": "3"}]',
        ),
        (
            "select.keba_keenergy_12345678_external_heat_source_operating_mode_1",
            "on",
            '[{"name": "APPL.CtrlAppl.sParam.extHeatSource[0].param.operatingMode", "value": "1"}]',
        ),
        (
            "select.keba_keenergy_12345678_external_heat_source_operating_mode_1",
            "flue",
            '[{"name": "APPL.CtrlAppl.sParam.extHeatSource[0].param.operatingMode", "value": "2"}]',
        ),
        (
            "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
            "HC FBH",
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.linTab.fileName", "value": "HC FBH"}]',
        ),
    ],
    ids=[
        "operating_mode",
        "heat_circuit_operating_mode",
        "solar_circuit_operating_mode",
        "hot_water_tank_operating_mode",
        "external_heat_source_operating_mode",
        "external_heat_source_operating_mode_flue",
        "heat_circuit_heating_curve",
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_select_option(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    option: str,
    expected: str,
) -> None:
    """Test selecting an option of a select entity."""
    fake_api.load_device("multiple_devices")
    fake_api.fixed_data = replace_values(fake_api.fixed_data, PASSIVE_COOLING_VALUES)
    await fake_api.setup_integration()

    await select_option(hass, entity_id, option)

    assert fake_api.write_requests() == [expected]


async def test_select_invalid_option(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the system operating mode rejects a cooling mode without a device that can cool."""
    fake_api.load_device("multiple_devices")
    fake_api.fixed_data = replace_values(fake_api.fixed_data, WITHOUT_COOLING_VALUES)
    await fake_api.setup_integration()

    with pytest.raises(
        ServiceValidationError,
        match=re.escape(
            "Option auto_cool is not valid for entity select.keba_keenergy_12345678_operating_mode, "
            "valid options are: standby, summer, auto_heat",
        ),
    ) as error:
        await select_option(hass, "select.keba_keenergy_12345678_operating_mode", "auto_cool")

    assert error.value.translation_key == "not_valid_option"

    assert fake_api.write_requests() == []


async def test_select_current_option_not_offered(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a select is unknown if the control unit is in a mode that the select does not offer."""
    fake_api.load_device("single_device")
    fake_api.data = replace_values(
        fake_api.data,
        {"APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode": str(HeatingCircuitOperatingMode.EXTERNAL.value)},
    )
    await fake_api.setup_integration()

    assert get_state(hass, "select.keba_keenergy_12345678_heat_circuit_operating_mode").state == STATE_UNKNOWN


@pytest.mark.usefixtures("init_integration")
async def test_select_unchanged_option(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the current option of a select entity is not written again."""
    await select_option(hass, "select.keba_keenergy_12345678_hot_water_tank_operating_mode_1", "heat_up")

    assert fake_api.write_requests() == []


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heating_curve_options_after_update(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the heating curve select drops a heating curve renamed on the control unit with the next update."""
    fake_api.load_device("multiple_devices")
    fake_api.responses = fake_api.setup_responses(fake_api.data, fake_api.data)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEATING_CURVE_ENTITY_ID)
    assert "HC1" in state.attributes[ATTR_OPTIONS]

    fake_api.curve_names = replace_values(fake_api.curve_names, CURVE_RENAMED_VALUES)
    fake_api.curve_points = replace_values(fake_api.curve_points, CURVE_RENAMED_VALUES)
    await next_update(hass, freezer)

    state = get_state(hass, HEATING_CURVE_ENTITY_ID)

    assert "HC1" not in state.attributes[ATTR_OPTIONS]
