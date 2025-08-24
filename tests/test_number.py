import pytest
from homeassistant.components.number import ATTR_VALUE
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number.const import SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests.api_data import MULTIPLE_POSITIONS_DATA_RESPONSE
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.parametrize(
    ("entity_id", "value", "expected"),
    [
        (
            "number.keba_keenergy_12345678_hot_water_tank_min_temperature_2",
            18,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[1].param.reducedSetTempMax.value", "value": "18.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_hot_water_tank_max_temperature_1",
            44,
            '[{"name": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value", "value": "44.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_day_temperature_1",
            22,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.normalSetTemp", "value": "22.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_night_temperature_1",
            16,
            '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.reducedSetTemp", "value": "16.0"}]',
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_holiday_temperature_1",
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
    """Test set value."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        MULTIPLE_POSITIONS_DATA_RESPONSE,
    ]
    fake_api.register_requests("10.0.0.100")

    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)

    state: State | None = hass.states.get(entity_id)
    assert isinstance(state, State)

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: entity_id,
            ATTR_VALUE: value,
        },
        blocking=True,
    )

    fake_api.assert_called_write_with(expected)
