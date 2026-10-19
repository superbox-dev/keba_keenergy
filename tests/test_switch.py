# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the switch entities."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
from homeassistant.components.switch.const import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.helpers import entity_registry as er
from keba_keenergy_api.constants import HeatCircuitMode

from tests import get_platform_states
from tests.api_data import ENTITY_UPDATED_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITION_OTHER_MODES_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response
from tests.api_data import update_response

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_switches(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all switch entities."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.SWITCH):
        assert state == snapshot(name=state.entity_id)


@pytest.mark.parametrize(
    ("entity_id", "response", "expected"),
    [
        (
            "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed",
            MULTIPLE_POSITION_OTHER_MODES_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed", "value": "1"}]',
        ),
        (
            "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_2",
            MULTIPLE_POSITION_OTHER_MODES_DATA_RESPONSE,
            (
                '[{"name": "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]", "value": "1"}, '
                '{"name": "APPL.CtrlAppl.sParam.genericHeat[2].param.priority", "value": "14"}]'
            ),
        ),
        (
            "switch.keba_keenergy_12345678_heat_circuit_use_heating_curve_1",
            MULTIPLE_POSITION_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.enableHeatCurveLinTab", "value": "1"}]',
        ),
        (
            "switch.keba_keenergy_12345678_heat_circuit_use_cooling_curve_2",
            ENTITY_UPDATED_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.enableHeatCurveLinTab", "value": "1"}]',
        ),
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_turn_on(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    response: list[dict[str, Any]],
    expected: str,
) -> None:
    """Test turning on a switch."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        response,
        # Read API after services call
        response,
    ]
    await fake_api.setup_integration()

    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    await hass.services.async_call(
        domain=SWITCH_DOMAIN,
        service=SERVICE_TURN_ON,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("entity_id", "response", "expected"),
    [
        (
            "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed",
            MULTIPLE_POSITION_DATA_RESPONSE,
            '[{"name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed", "value": "0"}]',
        ),
        (
            "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_2",
            MULTIPLE_POSITION_DATA_RESPONSE,
            (
                '[{"name": "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]", "value": "0"}, '
                '{"name": "APPL.CtrlAppl.sParam.genericHeat[2].param.priority", "value": "15"}]'
            ),
        ),
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_turn_off(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    response: list[dict[str, Any]],
    expected: str,
) -> None:
    """Test turning off a switch."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        response,
        # Read API after services call
        response,
    ]
    await fake_api.setup_integration()

    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    await hass.services.async_call(
        domain=SWITCH_DOMAIN,
        service=SERVICE_TURN_OFF,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("service", "response"),
    [
        (SERVICE_TURN_ON, MULTIPLE_POSITION_DATA_RESPONSE),
        (SERVICE_TURN_OFF, MULTIPLE_POSITION_OTHER_MODES_DATA_RESPONSE),
    ],
)
async def test_unchanged_state(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    service: str,
    response: list[dict[str, Any]],
) -> None:
    """Test that a switch is not written if it already has the state."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        response,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=SWITCH_DOMAIN,
        service=service,
        service_data={
            ATTR_ENTITY_ID: "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_2",
        },
        blocking=True,
    )

    assert fake_api.write_requests() == []


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heating_and_cooling_circuit_has_one_curve_switch(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a heating and cooling circuit only has the heating curve switch, because both use one setting."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        update_response(
            get_multiple_position_fixed_data_response(),
            "APPL.CtrlAppl.sParam.options.heatCircuit[1].type",
            value=str(HeatCircuitMode.HEATING_AND_COOLING.value),
        ),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    assert sorted(
        entry.unique_id
        for entry in er.async_entries_for_config_entry(er.async_get(hass), fake_api.config_entry.entry_id)
        if entry.domain == SWITCH_DOMAIN and "_curve_" in entry.unique_id
    ) == [
        "12345678_heat_circuit_use_heating_curve_1",
        "12345678_heat_circuit_use_heating_curve_2",
    ]
