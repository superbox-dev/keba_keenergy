from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

import pytest
from homeassistant.components.switch.const import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import CONF_HOST
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from homeassistant.core import State

from tests import setup_integration
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import HEATING_CURVE_NAMES_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_2
from tests.api_data import get_multiple_position_fixed_data_response

if TYPE_CHECKING:
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion
    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    "entity",
    [
        # buffer tank
        "switch.keba_keenergy_12345678_buffer_tank_use_excess_energy_1",
        "switch.keba_keenergy_12345678_buffer_tank_use_excess_energy_2",
        # hot water tank
        "switch.keba_keenergy_12345678_hot_water_tank_use_excess_energy_1",
        "switch.keba_keenergy_12345678_hot_water_tank_use_excess_energy_2",
        # heat pump
        "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed",
        # heating circuit
        "switch.keba_keenergy_12345678_heat_circuit_use_excess_energy_1",
        "switch.keba_keenergy_12345678_heat_circuit_use_excess_energy_2",
        "switch.keba_keenergy_12345678_heat_circuit_use_heating_curve_1",
        "switch.keba_keenergy_12345678_heat_circuit_use_heating_curve_2",
        # solar circuit
        "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_1",
        "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_2",
        # external heat source
        "switch.keba_keenergy_12345678_external_heat_source_use_excess_energy_1",
        "switch.keba_keenergy_12345678_external_heat_source_use_excess_energy_2",
    ],
)
@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_binary_sensors(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    language: str,
    entity: str,
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


@pytest.mark.parametrize(
    ("entity_id", "service", "response", "expected"),
    [
        (
            "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed",
            SERVICE_TURN_ON,
            MULTIPLE_POSITION_DATA_RESPONSE_2,
            '[{"name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed", "value": "1"}]',
        ),
        (
            "switch.keba_keenergy_12345678_heat_pump_compressor_use_night_speed",
            SERVICE_TURN_OFF,
            MULTIPLE_POSITION_DATA_RESPONSE_1,
            '[{"name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.useDayNightSpeed", "value": "0"}]',
        ),
        (
            "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_2",
            SERVICE_TURN_ON,
            MULTIPLE_POSITION_DATA_RESPONSE_2,
            '[{"name": "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]", "value": "1"}, '
            '{"name": "APPL.CtrlAppl.sParam.genericHeat[2].param.priority", "value": "14"}]',
        ),
        (
            "switch.keba_keenergy_12345678_solar_circuit_priority_1_before_2_2",
            SERVICE_TURN_OFF,
            MULTIPLE_POSITION_DATA_RESPONSE_1,
            '[{"name": "APPL.CtrlAppl.sParam.hmiRetainData.consumer1PrioritySolar[1]", "value": "0"}, '
            '{"name": "APPL.CtrlAppl.sParam.genericHeat[2].param.priority", "value": "15"}]',
        ),
        (
            "switch.keba_keenergy_12345678_heat_circuit_use_heating_curve_1",
            SERVICE_TURN_ON,
            MULTIPLE_POSITION_DATA_RESPONSE_1,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.enableHeatCurveLinTab", "value": "1"}]',
        ),
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_set_value(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    service: str,
    response: list[dict[str, Any]],
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        response,
        *HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        response,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    await hass.services.async_call(
        domain=SWITCH_DOMAIN,
        service=service,
        service_data={
            ATTR_ENTITY_ID: entity_id,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)
