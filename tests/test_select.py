# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the select entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import ServiceValidationError

from tests import get_option_translations
from tests import get_platform_states
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


# The options of these selects are the names of the heating curves on the Web HMI, so they are not translated
HEATING_CURVE_SELECTS: tuple[str, ...] = (
    "select.keba_keenergy_12345678_heat_circuit_cooling_curve_2",
    "select.keba_keenergy_12345678_heat_circuit_heating_curve_1",
)


@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_selects(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states and the translated options of all select entities, with cooling."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    for state in get_platform_states(hass, fake_api.config_entry, Platform.SELECT):
        assert state == snapshot(name=state.entity_id)

        if state.entity_id not in HEATING_CURVE_SELECTS:
            assert await get_option_translations(hass, state) == snapshot(name=f"{state.entity_id}_options")


@pytest.mark.parametrize("language", ["en", "de"], indirect=True)
@pytest.mark.usefixtures("language")
async def test_selects_without_cooling(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the operating mode selects of a setup without cooling."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="false", has_cooling_circuits=False),
        MULTIPLE_POSITION_DATA_RESPONSE,
    ]
    await fake_api.setup_integration()

    for entity_id in (
        "select.keba_keenergy_12345678_operating_mode",
        "select.keba_keenergy_12345678_heat_circuit_operating_mode_1",
        "select.keba_keenergy_12345678_heat_circuit_operating_mode_2",
    ):
        state: State | None = hass.states.get(entity_id)
        assert isinstance(state, State)
        assert state == snapshot(name=entity_id)
        assert await get_option_translations(hass, state) == snapshot(name=f"{entity_id}_options")


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
        MULTIPLE_POSITION_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE,
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
        MULTIPLE_POSITION_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE,
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
        MULTIPLE_POSITION_DATA_RESPONSE,
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
