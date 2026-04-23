from __future__ import annotations

from datetime import timedelta
from typing import Any
from typing import TYPE_CHECKING

import pytest
import voluptuous as vol
from homeassistant.components.number import ATTR_VALUE
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number.const import SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from tests import setup_integration
from tests.api_data import DEFAULT_POSITION_FIXED_DATA_RESPONSE
from tests.api_data import DEFAULT_POSITION_RESPONSE
from tests.api_data import HEATING_CURVES_RESPONSE_1_1
from tests.api_data import HEATING_CURVE_NAMES_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import get_multiple_position_fixed_data_response
from tests.api_data import get_single_position_data_response

if TYPE_CHECKING:
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion
    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    "entity",
    [
        # buffer tank
        "number.keba_keenergy_12345678_buffer_tank_excess_energy_target_temperature_1",
        "number.keba_keenergy_12345678_buffer_tank_excess_energy_target_temperature_2",
        "number.keba_keenergy_12345678_buffer_tank_excess_energy_target_temperature_hysteresis_1",
        "number.keba_keenergy_12345678_buffer_tank_excess_energy_target_temperature_hysteresis_2",
        "number.keba_keenergy_12345678_buffer_tank_outdoor_temperature_excess_energy_limit_1",
        "number.keba_keenergy_12345678_buffer_tank_outdoor_temperature_excess_energy_limit_2",
        "number.keba_keenergy_12345678_buffer_tank_standby_temperature_1",
        "number.keba_keenergy_12345678_buffer_tank_standby_temperature_2",
        # hot water tank
        "number.keba_keenergy_12345678_hot_water_tank_excess_energy_target_temperature_1",
        "number.keba_keenergy_12345678_hot_water_tank_excess_energy_target_temperature_2",
        "number.keba_keenergy_12345678_hot_water_tank_excess_energy_target_temperature_hysteresis_1",
        "number.keba_keenergy_12345678_hot_water_tank_excess_energy_target_temperature_hysteresis_2",
        "number.keba_keenergy_12345678_hot_water_tank_standby_temperature_1",
        "number.keba_keenergy_12345678_hot_water_tank_standby_temperature_2",
        "number.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
        "number.keba_keenergy_12345678_hot_water_tank_target_temperature_2",
        # heat pump
        "number.keba_keenergy_12345678_heat_pump_compressor_night_speed",
        # heating circuit
        "number.keba_keenergy_12345678_heat_circuit_cooling_curve_offset_2",
        "number.keba_keenergy_12345678_heat_circuit_cooling_curve_slope_2",
        "number.keba_keenergy_12345678_heat_circuit_cooling_limit_day_2",
        "number.keba_keenergy_12345678_heat_circuit_cooling_limit_night_2",
        "number.keba_keenergy_12345678_heat_circuit_excess_energy_cooling_limit_day_2",
        "number.keba_keenergy_12345678_heat_circuit_excess_energy_cooling_limit_night_2",
        "number.keba_keenergy_12345678_heat_circuit_excess_energy_heating_limit_day_1",
        "number.keba_keenergy_12345678_heat_circuit_excess_energy_heating_limit_night_1",
        "number.keba_keenergy_12345678_heat_circuit_excess_energy_target_cooling_temperature_2",
        "number.keba_keenergy_12345678_heat_circuit_excess_energy_target_cooling_temperature_hysteresis_2",
        "number.keba_keenergy_12345678_heat_circuit_excess_energy_target_temperature_1",
        "number.keba_keenergy_12345678_heat_circuit_excess_energy_target_temperature_hysteresis_1",
        "number.keba_keenergy_12345678_heat_circuit_heating_curve_offset_1",
        "number.keba_keenergy_12345678_heat_circuit_heating_curve_slope_1",
        "number.keba_keenergy_12345678_heat_circuit_heating_limit_day_1",
        "number.keba_keenergy_12345678_heat_circuit_heating_limit_night_1",
        "number.keba_keenergy_12345678_heat_circuit_target_cooling_temperature_day_2",
        "number.keba_keenergy_12345678_heat_circuit_target_cooling_temperature_night_2",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_away_1",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_night_1",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1",
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_offset_2",
        # solar circuit
        "number.keba_keenergy_12345678_solar_circuit_target_temperature_1_1",
        "number.keba_keenergy_12345678_solar_circuit_target_temperature_1_2",
        "number.keba_keenergy_12345678_solar_circuit_target_temperature_2_1",
        "number.keba_keenergy_12345678_solar_circuit_target_temperature_2_2",
        # external heat source
        "number.keba_keenergy_12345678_external_heat_source_min_runtime_excess_energy_1",
        "number.keba_keenergy_12345678_external_heat_source_min_runtime_excess_energy_2",
    ],
)
@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_numbers(
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
    ("entity_id", "value", "expected"),
    [
        (
            "number.keba_keenergy_12345678_solar_circuit_target_temperature_1_2",
            18,
            '[{"name": "APPL.CtrlAppl.sParam.genericHeat[2].param.setTempMax.value", "value": "18.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_solar_circuit_target_temperature_2_2",
            22,
            '[{"name": "APPL.CtrlAppl.sParam.genericHeat[3].param.setTempMax.value", "value": "22.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_buffer_tank_standby_temperature_1",
            11,
            '[{"name": "APPL.CtrlAppl.sParam.bufferTank[0].param.backupTemp", "value": "11.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_hot_water_tank_standby_temperature_2",
            18,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[1].param.reducedSetTempMax.value", "value": "18.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
            44,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", "value": "44.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
            22,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.normalSetTemp", "value": "22.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_night_1",
            16,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.reducedSetTemp", "value": "16.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_away_1",
            14,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.holidaySetTemp", "value": "14.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1",
            0.5,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp", "value": "0.5"}]',
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_heating_curve_offset_1",
            5.5,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.heatCurveOffset", "value": "5.5"}]',
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_heating_curve_slope_1",
            0.3,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.heatCurveGradient", "value": "0.3"}]',
        ),
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_set_value(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: int,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
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
        domain=NUMBER_DOMAIN,
        service=SERVICE_SET_VALUE,
        service_data={
            ATTR_ENTITY_ID: entity_id,
            ATTR_VALUE: value,
        },
        blocking=True,
    )

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))
    await hass.async_block_till_done()

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("entity_id", "value", "expected"),
    [
        (
            "number.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
            100,
            r"Value 100\.0 for number\.keba_keenergy_12345678_hot_water_tank_target_temperature_1 "
            r"is outside valid range 0\.0 - 52\.0",
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
            -10,
            r"Value -10\.0 for number\.keba_keenergy_12345678_heat_circuit_target_temperature_day_1 "
            r"is outside valid range 10\.0 - 30\.0",
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1",
            -3,
            r"Value -3\.0 for number\.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1 "
            r"is outside valid range -2\.5 - 2\.5",
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_heating_curve_offset_1",
            -11,
            r"Value -11\.0 for number\.keba_keenergy_12345678_heat_circuit_heating_curve_offset_1 "
            r"is outside valid range -10\.0 - 10\.0",
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_heating_curve_slope_1",
            -0.1,
            r"Value -0\.1 for number\.keba_keenergy_12345678_heat_circuit_heating_curve_slope_1 "
            r"is outside valid range 0\.0 - 5\.0",
        ),
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_set_value_bad_range(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: int,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    with pytest.raises(ServiceValidationError, match=expected):
        await hass.services.async_call(
            domain=NUMBER_DOMAIN,
            service=SERVICE_SET_VALUE,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_VALUE: value,
            },
            blocking=True,
        )


@pytest.mark.parametrize(
    ("entity_id", "value", "expected"),
    [
        (
            "number.keba_keenergy_12345678_hot_water_tank_max_temperature_1",
            None,
            r"expected float for dictionary value @ data\['value']",
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_day_temperature_1",
            "bad",
            r"expected float for dictionary value @ data\['value']",
        ),
    ],
)
async def test_set_value_bad_attr(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: Any,
    expected: str,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    with pytest.raises(vol.Invalid, match=expected):
        await hass.services.async_call(
            domain=NUMBER_DOMAIN,
            service=SERVICE_SET_VALUE,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_VALUE: value,
            },
            blocking=True,
        )


async def test_number_native_value_uses_pending_value(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        DEFAULT_POSITION_RESPONSE,
        HEATING_CURVE_NAMES_RESPONSE,
        DEFAULT_POSITION_FIXED_DATA_RESPONSE,
        get_single_position_data_response(heat_circuit_target_temperature_offset="1.5"),
        *HEATING_CURVES_RESPONSE_1_1,
        get_single_position_data_response(heat_circuit_target_temperature_offset="1.0"),
        *HEATING_CURVES_RESPONSE_1_1,
        get_single_position_data_response(heat_circuit_target_temperature_offset="0.5"),
        *HEATING_CURVES_RESPONSE_1_1,
    ]
    fake_api.register_requests(config_entry.data["host"])

    await setup_integration(hass, config_entry)

    entity = hass.data["number"].get_entity("number.keba_keenergy_12345678_heat_circuit_target_temperature_offset")
    assert entity is not None

    assert entity.native_value == 1.5

    # First call → creates debounce handle
    await entity.async_set_native_value(1.0)
    first_handle = entity._async_call_later

    assert first_handle is not None
    assert entity.native_value == 1.0

    # Second call BEFORE debounce fires
    await entity.async_set_native_value(0.5)

    assert entity._async_call_later is not None
    assert entity._async_call_later is not first_handle
    assert entity.native_value == 0.5
