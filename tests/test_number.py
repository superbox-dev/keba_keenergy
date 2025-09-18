from typing import Any

import pytest
import voluptuous as vol
from homeassistant.components.number import ATTR_VALUE
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number.const import SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    ("entity_id", "value", "expected"),
    [
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
    ],
)
async def test_set_value(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: int,
    expected: str,
) -> None:
    """Test the setting of the value."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
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

    fake_api.assert_called_write_with(expected)


@pytest.mark.parametrize(
    ("entity_id", "value", "expected"),
    [
        (
            "number.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
            100,
            "Value 100.0 for number.keba_keenergy_12345678_hot_water_tank_target_temperature_1 "
            "is outside valid range 0.0 - 52.0",
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
            -10,
            "Value -10.0 for number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1 "
            "is outside valid range 10.0 - 30.0",
        ),
    ],
)
async def test_set_value_bad_range(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: int,
    expected: str,
) -> None:
    """Test setting the value out of range."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    with pytest.raises(ServiceValidationError) as error:
        await hass.services.async_call(
            domain=NUMBER_DOMAIN,
            service=SERVICE_SET_VALUE,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_VALUE: value,
            },
            blocking=True,
        )

    assert str(error.value) == expected


@pytest.mark.parametrize(
    ("entity_id", "value", "expected"),
    [
        (
            "number.keba_keenergy_12345678_hot_water_tank_max_temperature_1",
            None,
            "expected float for dictionary value @ data['value']",
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_day_temperature_1",
            "bad",
            "expected float for dictionary value @ data['value']",
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
    """Test setting the value without required attribute."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    await setup_integration(hass, config_entry)

    with pytest.raises(vol.Invalid) as error:
        await hass.services.async_call(
            domain=NUMBER_DOMAIN,
            service=SERVICE_SET_VALUE,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_VALUE: value,
            },
            blocking=True,
        )

    assert str(error.value) == expected
