from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.components.sensor.const import ATTR_OPTIONS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import ServiceValidationError

from tests import init_translations
from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import HEATING_CURVE_NAMES_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from pytest_homeassistant_custom_component.common import MockConfigEntry
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
@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_selects(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    language: str,
    entity: str,
    translation: str | None,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])
    hass.config.language = language

    await setup_integration(hass, config_entry)

    _entity: State | None = hass.states.get(entity)
    assert isinstance(_entity, State)
    assert _entity == snapshot

    if translation:
        translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

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
@pytest.mark.parametrize("language", ["en", "de"])
async def test_selects_with_cooling(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    language: str,
    entity: str,
    translation: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])
    hass.config.language = language

    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

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
@pytest.mark.parametrize("language", ["en", "de"])
async def test_selects_without_cooling(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    language: str,
    entity: str,
    translation: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="false"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])
    hass.config.language = language

    await setup_integration(hass, config_entry)
    translations: dict[str, str] = await init_translations(hass, config_entry, category="entity")

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
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    option: int,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="true"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

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
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    option: int,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(has_passive_cooling="false"),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

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
