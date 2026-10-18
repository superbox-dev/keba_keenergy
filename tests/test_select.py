# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the select entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import ServiceValidationError

from tests import init_translations
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    ("entity", "translation"),
    [
        # buffer tank
        ("select.keba_keenergy_12345678_buffer_tank_operating_mode_1", "buffer_tank_operating_mode"),
        ("select.keba_keenergy_12345678_buffer_tank_operating_mode_2", "buffer_tank_operating_mode"),
        # hot water tank
        ("select.keba_keenergy_12345678_hot_water_tank_operating_mode_1", "hot_water_tank_operating_mode"),
        ("select.keba_keenergy_12345678_hot_water_tank_operating_mode_2", "hot_water_tank_operating_mode"),
        # heating circuit
        ("select.keba_keenergy_12345678_heat_circuit_cooling_curve_2", None),
        ("select.keba_keenergy_12345678_heat_circuit_heating_curve_1", None),
        # solar circuit
        ("select.keba_keenergy_12345678_solar_circuit_operating_mode_1", "solar_circuit_operating_mode"),
        ("select.keba_keenergy_12345678_solar_circuit_operating_mode_2", "solar_circuit_operating_mode"),
        # external heat source
        ("select.keba_keenergy_12345678_external_heat_source_operating_mode_1", "external_heat_source_operating_mode"),
        ("select.keba_keenergy_12345678_external_heat_source_operating_mode_2", "external_heat_source_operating_mode"),
    ],
)
@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_selects(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    entity: str,
    translation: str | None,
) -> None:
    """Test the states and the translated options of the select entities."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]

    await fake_api.setup_integration()

    _entity: State | None = hass.states.get(entity)
    assert isinstance(_entity, State)
    assert _entity == snapshot

    if translation:
        translations: dict[str, str] = await init_translations(hass, category="entity")

        assert {
            opt: translations[f"component.keba_keenergy.entity.select.{translation}.state.{opt}"]
            for opt in _entity.attributes[ATTR_OPTIONS]
        } == snapshot


@pytest.mark.parametrize(
    ("entity", "translation"),
    [
        # system
        ("select.keba_keenergy_12345678_operating_mode", "system_operating_mode"),
        # heating circuit
        ("select.keba_keenergy_12345678_heat_circuit_operating_mode_1", "heat_circuit_operating_mode"),
        ("select.keba_keenergy_12345678_heat_circuit_operating_mode_2", "heat_circuit_operating_mode"),
    ],
)
@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("language")
async def test_selects_with_cooling(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    entity: str,
    translation: str,
) -> None:
    """Test the select entities of heating circuits with cooling."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]

    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="entity")

    _entity: State | None = hass.states.get(entity)
    assert isinstance(_entity, State)
    assert _entity == snapshot
    assert {
        opt: translations[f"component.keba_keenergy.entity.select.{translation}.state.{opt}"]
        for opt in _entity.attributes[ATTR_OPTIONS]
    } == snapshot


@pytest.mark.parametrize(
    ("entity", "translation"),
    [
        # system
        ("select.keba_keenergy_12345678_operating_mode", "system_operating_mode"),
        # heating circuit
        ("select.keba_keenergy_12345678_heat_circuit_operating_mode_1", "heat_circuit_operating_mode"),
        ("select.keba_keenergy_12345678_heat_circuit_operating_mode_2", "heat_circuit_operating_mode"),
    ],
)
@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("language")
async def test_selects_without_cooling(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    entity: str,
    translation: str,
) -> None:
    """Test the select entities of heating circuits without cooling."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="false", has_cooling_circuits=False),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]

    await fake_api.setup_integration()
    translations: dict[str, str] = await init_translations(hass, category="entity")

    _entity: State | None = hass.states.get(entity)
    assert isinstance(_entity, State)
    assert _entity == snapshot
    assert {
        opt: translations[f"component.keba_keenergy.entity.select.{translation}.state.{opt}"]
        for opt in _entity.attributes[ATTR_OPTIONS]
    } == snapshot


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
            "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
            "HC FBH",
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.linTab.fileName", "value": "HC FBH"}]',
        ),
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_select_option(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    option: int,
    expected: str,
) -> None:
    """Test selecting an option of a select entity."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_OPTION: option,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("entity_id", "option", "expected"),
    [
        (
            "select.keba_keenergy_12345678_operating_mode",
            "auto_cool",
            (
                "Option auto_cool is not valid for entity select.keba_keenergy_12345678_operating_mode, "
                "valid options are: standby, summer, auto_heat"
            ),
        ),
    ],
)
async def test_select_invalid_option(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    option: int,
    expected: str,
) -> None:
    """Test selecting an invalid option of a select entity."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="false", has_cooling_circuits=False),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    with pytest.raises(ServiceValidationError, match=expected):
        await hass.services.async_call(
            domain=SELECT_DOMAIN,
            service=SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_OPTION: option,
            },
            blocking=True,
        )


async def test_select_unchanged_option(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the current option of a select entity is not written again."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=SELECT_DOMAIN,
        service=SERVICE_SELECT_OPTION,
        service_data={
            ATTR_ENTITY_ID: "select.keba_keenergy_12345678_hot_water_tank_operating_mode_1",
            ATTR_OPTION: "heat_up",
        },
        blocking=True,
    )

    assert fake_api.write_requests() == []
