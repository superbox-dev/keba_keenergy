# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import async_rounded_state
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.const import ATTR_UNIT_OF_MEASUREMENT
from homeassistant.const import STATE_UNKNOWN
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er

from custom_components.keba_keenergy.const import ATTR_POINTS
from custom_components.keba_keenergy.const import DOMAIN
from tests import get_option_translations
from tests import get_platform_states
from tests import get_state
from tests.api_data import CURVES_WITHOUT_NAMES_RESPONSE
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import get_multiple_devices_responses
from tests.api_data import update_response

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_sensors(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all sensors, their displayed values and the translated options of the enum sensors."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE, has_passive_cooling="true")
    await fake_api.setup_integration()

    states: list[State] = get_platform_states(hass, fake_api.config_entry, Platform.SENSOR)
    enum_states: list[State] = [state for state in states if ATTR_OPTIONS in state.attributes]
    value_states: list[State] = [state for state in states if ATTR_OPTIONS not in state.attributes]

    for state in states:
        assert state == snapshot(name=state.entity_id)

    for state in enum_states:
        assert await get_option_translations(hass, state) == snapshot(name=f"{state.entity_id}_options")

    for state in value_states:
        # The value as Home Assistant shows it, rounded to the display precision of the entity, with its unit.
        displayed: str = " ".join(
            filter(
                None,
                (async_rounded_state(hass, state.entity_id, state), state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)),
            ),
        )
        assert displayed == snapshot(name=f"{state.entity_id}_displayed")


@pytest.mark.parametrize(
    ("unique_id", "expected"),
    [
        ("12345678_heat_pump_operating_time", ("1058.06333333333", "h")),
        ("12345678_photovoltaics_daily_energy", ("437.699972222222", "kWh")),
        ("12345678_heat_pump_heating_power", ("3.2187521", "W")),
    ],
    ids=["heat_pump_operating_time", "photovoltaics_daily_energy", "heat_pump_heating_power"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_converted_sensor_keeps_registered_unit(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    unique_id: str,
    expected: tuple[str, str],
) -> None:
    """Test that an existing sensor keeps the unit it was registered with before the unit came from the endpoint."""
    config_entry.add_to_hass(hass)
    entry: er.RegistryEntry = er.async_get(hass).async_get_or_create(
        SENSOR_DOMAIN,
        DOMAIN,
        unique_id,
        config_entry=config_entry,
        suggested_object_id=f"{DOMAIN}_{unique_id}",
        unit_of_measurement=expected[1],
    )
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    state: State = get_state(hass, entry.entity_id)
    assert (state.state, state.attributes[ATTR_UNIT_OF_MEASUREMENT]) == expected


@pytest.mark.parametrize(
    ("message_id", "expected"),
    [
        (
            "APPL.CtrlAppl.sParam.outdoorTemp.state.msgId",
            {"sensor.keba_keenergy_12345678_outdoor_temperature": STATE_UNKNOWN},
        ),
        (
            # The mixer flow temperature has a new key in the API, but keeps the entity of the old key.
            "APPL.CtrlAppl.sParam.heatCircuit[0].heatCircuitMixer.flowTemp.state.msgId",
            {"sensor.keba_keenergy_12345678_heat_circuit_flow_temperature_1": STATE_UNKNOWN},
        ),
        (
            # Each solar circuit has two temperatures, the first of the second solar circuit is not in use.
            "APPL.CtrlAppl.sParam.genericHeat[2].referenceTemp.state.msgId",
            {
                "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_1": "36.799999",
                "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_1": "26.799999",
                "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_2": STATE_UNKNOWN,
                "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_2": "56.799999",
            },
        ),
        (
            # The mixer position has no setpoint for its attributes.
            "APPL.CtrlAppl.sParam.heatCircuit[0].heatCircuitMixer.mixer.state.msgId",
            {"sensor.keba_keenergy_12345678_heat_circuit_mixer_position_1": STATE_UNKNOWN},
        ),
    ],
    ids=[
        "outdoor_temperature",
        "heating_circuit_flow_temperature",
        "solar_circuit_current_temperature",
        "heating_circuit_mixer_position",
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor_not_in_use(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    message_id: str,
    expected: dict[str, str],
) -> None:
    """Test that a sensor is unknown if the control unit reports it as not in use."""
    fake_api.message_ids = {message_id: 50}
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    states: dict[str, str] = {}

    for entity_id in expected:
        state: State = get_state(hass, entity_id)
        states[entity_id] = state.state

    assert states == expected


@pytest.mark.parametrize(
    ("message_id", "entity_id"),
    [
        ("APPL.CtrlAppl.sParam.outdoorTemp.state.msgId", "sensor.keba_keenergy_12345678_outdoor_temperature"),
        (
            # Each solar circuit has two temperatures, the first of the second solar circuit is deactivated.
            "APPL.CtrlAppl.sParam.genericHeat[2].referenceTemp.state.msgId",
            "sensor.keba_keenergy_12345678_solar_circuit_current_temperature_1_2",
        ),
    ],
    ids=["outdoor_temperature", "solar_circuit_current_temperature"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor_deactivated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    message_id: str,
    entity_id: str,
) -> None:
    """Test that the entity of a deactivated sensor is removed and no longer created."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    entity_registry: er.EntityRegistry = er.async_get(hass)
    assert entity_registry.async_get(entity_id) is not None

    fake_api.message_ids = {message_id: 10}
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert entity_registry.async_get(entity_id) is None
    assert hass.states.get(entity_id) is None
    assert hass.states.get("sensor.keba_keenergy_12345678_solar_circuit_current_temperature_2_2") is not None


@pytest.mark.parametrize(
    ("value", "entity_id", "expected"),
    [
        (
            ("APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState", "9"),
            "sensor.keba_keenergy_12345678_heat_pump_state",
            "source_flush",
        ),
        (
            ("APPL.CtrlAppl.sParam.extHeatSource[0].param.operatingMode", "2"),
            "sensor.keba_keenergy_12345678_external_heat_source_operating_mode_1",
            "flue",
        ),
    ],
    ids=["heat_pump_state_source_flush", "external_heat_source_operating_mode_flue"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor_enum_state(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    value: tuple[str, str],
    entity_id: str,
    expected: str,
) -> None:
    """Test the enum sensor states that are only reported in rare situations."""
    name, raw_value = value
    fake_api.responses = get_multiple_devices_responses(
        update_response(MULTIPLE_DEVICES_DATA_RESPONSE, name, value=raw_value),
    )
    await fake_api.setup_integration()

    state: State = get_state(hass, entity_id)
    assert state.state == expected
    assert expected in state.attributes[ATTR_OPTIONS]


@pytest.mark.parametrize(
    ("value", "entity_id", "expected"),
    [
        (
            ("APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpSubState", "25"),
            "sensor.keba_keenergy_12345678_heat_pump_substate",
            ("drip", {"raw_value": 25}),
        ),
        (
            ("APPL.CtrlAppl.sParam.heatCircuit[0].heatCircuitMixer.mixer.values.setValueScaled", "0.37"),
            "sensor.keba_keenergy_12345678_heat_circuit_mixer_position_1",
            ("off", {"raw_value": 0.37, "position_percent": 37}),
        ),
    ],
    ids=["heat_pump_substate_second_value", "heat_circuit_mixer_partly_open"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor_raw_value(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    value: tuple[str, str],
    entity_id: str,
    expected: tuple[str, dict[str, float]],
) -> None:
    """Test that `raw_value` is the value read, also for enum members with several values and mixer positions."""
    name, raw_value = value
    fake_api.responses = get_multiple_devices_responses(
        update_response(MULTIPLE_DEVICES_DATA_RESPONSE, name, value=raw_value),
    )
    await fake_api.setup_integration()

    state: State = get_state(hass, entity_id)
    expected_state, expected_attributes = expected
    assert state.state == expected_state
    assert {key: state.attributes.get(key) for key in expected_attributes} == expected_attributes


async def test_curve_sensor_without_curve(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a curve sensor has no points if its curve is no longer on the control unit."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    # The control unit has no curves, so the curves in use (e.g. `HC6`) do not exist.
    fake_api.curves = CURVES_WITHOUT_NAMES_RESPONSE
    await fake_api.setup_integration()

    state: State = get_state(hass, "sensor.keba_keenergy_12345678_heat_circuit_heating_curve_1")

    assert state.state == "HC6"
    assert state.attributes[ATTR_POINTS] == []
