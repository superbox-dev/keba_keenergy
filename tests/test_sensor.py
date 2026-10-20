# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.const import STATE_UNKNOWN
from homeassistant.const import Platform
from homeassistant.core import State
from homeassistant.helpers import entity_registry as er

from tests import get_option_translations
from tests import get_platform_states
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_sensors(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all sensors and the translated options of the enum sensors."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.SENSOR):
        assert state == snapshot(name=state.entity_id)

        if ATTR_OPTIONS in state.attributes:
            assert await get_option_translations(hass, state) == snapshot(name=f"{state.entity_id}_options")


@pytest.mark.parametrize(
    "entity_id",
    [
        "sensor.keba_keenergy_12345678_heat_pump_operating_time",
        "sensor.keba_keenergy_12345678_photovoltaics_daily_energy",
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_converted_sensor_display_precision(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
) -> None:
    """Test that converted sensors keep the exact value and are displayed with two decimals."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    entry: er.RegistryEntry | None = er.async_get(hass).async_get(entity_id)
    assert entry is not None
    assert entry.options["sensor"] == {"suggested_display_precision": 2}


@pytest.mark.parametrize(
    ("message_id", "expected"),
    [
        (
            "APPL.CtrlAppl.sParam.outdoorTemp.state.msgId",
            {"sensor.keba_keenergy_12345678_outdoor_temperature": (STATE_UNKNOWN, 10)},
        ),
        (
            # The mixer flow temperature has a new key in the API, but keeps the entity of the old key
            "APPL.CtrlAppl.sParam.heatCircuit[0].heatCircuitMixer.flowTemp.state.msgId",
            {"sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_1": (STATE_UNKNOWN, 10)},
        ),
        (
            # Each solar circuit has two temperatures, the first of the second solar circuit is not in use
            "APPL.CtrlAppl.sParam.genericHeat[2].referenceTemp.state.msgId",
            {
                "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_1": ("36.76", 0),
                "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_1": ("26.76", 0),
                "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_2": (STATE_UNKNOWN, 10),
                "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_2": ("56.76", 0),
            },
        ),
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor_not_in_use(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    message_id: str,
    expected: dict[str, tuple[str, int]],
) -> None:
    """Test that a sensor is unknown and has the message id if the control unit reports it as not in use."""
    fake_api.message_ids = {message_id: 10}
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    states: dict[str, tuple[str, int]] = {}

    for entity_id in expected:
        state: State | None = hass.states.get(entity_id)
        assert isinstance(state, State)
        states[entity_id] = (state.state, state.attributes["message_id"])

    assert states == expected
