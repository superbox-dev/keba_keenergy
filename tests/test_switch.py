# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the switch entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.switch.const import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er
from keba_keenergy_api.enums import HeatingCircuitType

from tests import get_platform_states
from tests.api_data import ENTITY_UPDATED_DATA_RESPONSE
from tests.api_data import HEAT_CIRCUIT_MODE
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_RESPONSE
from tests.api_data import Response
from tests.api_data import get_multiple_devices_fixed_data_response
from tests.api_data import get_multiple_devices_responses
from tests.api_data import replace_values
from tests.test_switch_data import COMPRESSOR_USE_NIGHT_SPEED_ENTITY_ID
from tests.test_switch_data import SOLAR_PRIORITY_ENTITY_ID
from tests.test_switch_data import USE_COOLING_CURVE_ENTITY_ID
from tests.test_switch_data import USE_HEATING_CURVE_ENTITY_ID

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_switches(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all switch entities."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE, has_passive_cooling="true")
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.SWITCH):
        assert state == snapshot(name=state.entity_id)


@pytest.mark.parametrize(
    ("service_call", "response", "expected_writes"),
    [
        (
            (SERVICE_TURN_ON, COMPRESSOR_USE_NIGHT_SPEED_ENTITY_ID),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            ['[{"name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed", "value": "1"}]'],
        ),
        (
            (SERVICE_TURN_OFF, COMPRESSOR_USE_NIGHT_SPEED_ENTITY_ID),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            ['[{"name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed", "value": "0"}]'],
        ),
        (
            (SERVICE_TURN_ON, SOLAR_PRIORITY_ENTITY_ID),
            MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE,
            [
                (
                    '[{"name": "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]", "value": "1"}, '
                    '{"name": "APPL.CtrlAppl.sParam.genericHeat[2].param.priority", "value": "14"}]'
                ),
            ],
        ),
        (
            (SERVICE_TURN_OFF, SOLAR_PRIORITY_ENTITY_ID),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            [
                (
                    '[{"name": "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]", "value": "0"}, '
                    '{"name": "APPL.CtrlAppl.sParam.genericHeat[2].param.priority", "value": "15"}]'
                ),
            ],
        ),
        ((SERVICE_TURN_ON, SOLAR_PRIORITY_ENTITY_ID), MULTIPLE_DEVICES_DATA_RESPONSE, []),
        ((SERVICE_TURN_OFF, SOLAR_PRIORITY_ENTITY_ID), MULTIPLE_DEVICES_OTHER_MODES_DATA_RESPONSE, []),
        (
            (SERVICE_TURN_ON, USE_HEATING_CURVE_ENTITY_ID),
            MULTIPLE_DEVICES_DATA_RESPONSE,
            ['[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.enableHeatCurveLinTab", "value": "1"}]'],
        ),
        (
            (SERVICE_TURN_ON, USE_COOLING_CURVE_ENTITY_ID),
            ENTITY_UPDATED_DATA_RESPONSE,
            ['[{"name": "APPL.CtrlAppl.sParam.heatCircuit[1].param.enableHeatCurveLinTab", "value": "1"}]'],
        ),
    ],
    ids=[
        "compressor_use_night_speed_turn_on",
        "compressor_use_night_speed_turn_off",
        "solar_circuit_priority_turn_on",
        "solar_circuit_priority_turn_off",
        "solar_circuit_priority_turn_on_unchanged",
        "solar_circuit_priority_turn_off_unchanged",
        "heat_circuit_use_heating_curve_turn_on",
        "heat_circuit_use_cooling_curve_turn_on",
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_turn_on_off(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    service_call: tuple[str, str],
    response: Response,
    expected_writes: list[str],
) -> None:
    """Test turning on and off a switch, a switch that already has the state is not written."""
    fake_api.responses = get_multiple_devices_responses(response)
    await fake_api.setup_integration()

    service, entity_id = service_call
    await hass.services.async_call(
        domain=SWITCH_DOMAIN,
        service=service,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    assert fake_api.write_requests() == expected_writes


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_heating_and_cooling_circuit_has_one_curve_switch(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a heating and cooling circuit only has the heating curve switch, because both use one setting."""
    fake_api.responses = [
        MULTIPLE_DEVICES_RESPONSE,
        replace_values(
            get_multiple_devices_fixed_data_response(),
            HEAT_CIRCUIT_MODE.read(str(HeatingCircuitType.HEATING_AND_COOLING.value), index=1),
        ),
        MULTIPLE_DEVICES_DATA_RESPONSE,
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
