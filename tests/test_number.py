from typing import Any

import pytest
import voluptuous as vol
from homeassistant.components.input_number import ATTR_MAX
from homeassistant.components.input_number import ATTR_MIN
from homeassistant.components.input_number import ATTR_STEP
from homeassistant.components.number import ATTR_VALUE
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number.const import SERVICE_SET_VALUE
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.const import CONF_DEVICE_CLASS
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT
from homeassistant.const import PERCENTAGE
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.core import State
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests import setup_integration
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import get_multi_positions_data_response
from tests.conftest import FakeKebaKeEnergyAPI


async def test_hot_water_tank_numbers(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test hot water tank numbers."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    hot_water_tank_standby_temperature_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_hot_water_tank_standby_temperature_1",
    )
    assert isinstance(hot_water_tank_standby_temperature_1, State)
    assert hot_water_tank_standby_temperature_1.attributes[ATTR_MIN] == 0.0
    assert hot_water_tank_standby_temperature_1.attributes[ATTR_MAX] == 52.0
    assert hot_water_tank_standby_temperature_1.attributes[ATTR_STEP] == 0.5
    assert hot_water_tank_standby_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_standby_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_standby_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 1 Standby temperature"

    hot_water_tank_target_temperature_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
    )
    assert isinstance(hot_water_tank_target_temperature_1, State)
    assert hot_water_tank_target_temperature_1.attributes[ATTR_MIN] == 0.0
    assert hot_water_tank_target_temperature_1.attributes[ATTR_MAX] == 52.0
    assert hot_water_tank_target_temperature_1.attributes[ATTR_STEP] == 0.5
    assert hot_water_tank_target_temperature_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert hot_water_tank_target_temperature_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert hot_water_tank_target_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Hot water tank 1 Target temperature"


async def test_hot_water_tank_numbers_translated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test hot water tank numbers translated."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    hot_water_tank_standby_temperature_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_hot_water_tank_standby_temperature_1",
    )
    assert isinstance(hot_water_tank_standby_temperature_1, State)
    assert hot_water_tank_standby_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 1 Stütztemperatur"

    hot_water_tank_target_temperature_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
    )
    assert isinstance(hot_water_tank_target_temperature_1, State)
    assert hot_water_tank_target_temperature_1.attributes[ATTR_FRIENDLY_NAME] == "Warmwasserspeicher 1 Soll-Temperatur"


async def test_heat_pump_numbers(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test heat pump numbers."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    heat_pump_compressor_night_speed: State | None = hass.states.get(
        "number.keba_keenergy_12345678_heat_pump_compressor_night_speed",
    )
    assert isinstance(heat_pump_compressor_night_speed, State)
    assert heat_pump_compressor_night_speed.attributes[ATTR_MIN] == 50.0
    assert heat_pump_compressor_night_speed.attributes[ATTR_MAX] == 100.0
    assert heat_pump_compressor_night_speed.attributes[ATTR_STEP] == 1
    assert heat_pump_compressor_night_speed.attributes[CONF_UNIT_OF_MEASUREMENT] == PERCENTAGE
    assert heat_pump_compressor_night_speed.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.SPEED
    assert heat_pump_compressor_night_speed.attributes[ATTR_FRIENDLY_NAME] == "Heat pump Compressor speed (night)"


async def test_heat_pump_numbers_translated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test heat pump numbers translated."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    heat_pump_compressor_night_speed: State | None = hass.states.get(
        "number.keba_keenergy_12345678_heat_pump_compressor_night_speed",
    )
    assert isinstance(heat_pump_compressor_night_speed, State)
    assert heat_pump_compressor_night_speed.attributes[ATTR_FRIENDLY_NAME] == "Wärmepumpe Kompressor-Drehzahl (Nacht)"


async def test_heat_circuit_numbers(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test heat circuit numbers."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    await setup_integration(hass, config_entry)

    heat_circuit_target_temperature_away_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_away_1",
    )
    assert isinstance(heat_circuit_target_temperature_away_1, State)
    assert heat_circuit_target_temperature_away_1.attributes[ATTR_MIN] == 10.0
    assert heat_circuit_target_temperature_away_1.attributes[ATTR_MAX] == 30.0
    assert heat_circuit_target_temperature_away_1.attributes[ATTR_STEP] == 0.5
    assert heat_circuit_target_temperature_away_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_target_temperature_away_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_target_temperature_away_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Target temperature (away)"
    )

    heat_circuit_target_temperature_day_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
    )
    assert isinstance(heat_circuit_target_temperature_day_1, State)
    assert heat_circuit_target_temperature_day_1.attributes[ATTR_MIN] == 10.0
    assert heat_circuit_target_temperature_day_1.attributes[ATTR_MAX] == 30.0
    assert heat_circuit_target_temperature_day_1.attributes[ATTR_STEP] == 0.5
    assert heat_circuit_target_temperature_day_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_target_temperature_day_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_target_temperature_day_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Target temperature (day)"
    )

    heat_circuit_target_temperature_night_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_night_1",
    )
    assert isinstance(heat_circuit_target_temperature_night_1, State)
    assert heat_circuit_target_temperature_night_1.attributes[ATTR_MIN] == 10.0
    assert heat_circuit_target_temperature_night_1.attributes[ATTR_MAX] == 30.0
    assert heat_circuit_target_temperature_night_1.attributes[ATTR_STEP] == 0.5
    assert heat_circuit_target_temperature_night_1.attributes[CONF_UNIT_OF_MEASUREMENT] == UnitOfTemperature.CELSIUS
    assert heat_circuit_target_temperature_night_1.attributes[CONF_DEVICE_CLASS] == SensorDeviceClass.TEMPERATURE
    assert (
        heat_circuit_target_temperature_night_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heating circuit 1 Target temperature (night)"
    )


async def test_heat_circuit_numbers_translated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test heat circuit numbers translated."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
    ]
    fake_api.register_requests(config_entry.data[CONF_HOST])

    hass.config.language = "de"
    await setup_integration(hass, config_entry)

    heat_circuit_target_temperature_away_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_away_1",
    )
    assert isinstance(heat_circuit_target_temperature_away_1, State)
    assert (
        heat_circuit_target_temperature_away_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heizkreis 1 Soll-Raumtemperatur (Urlaub)"
    )

    heat_circuit_target_temperature_day_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
    )
    assert isinstance(heat_circuit_target_temperature_day_1, State)
    assert (
        heat_circuit_target_temperature_day_1.attributes[ATTR_FRIENDLY_NAME] == "Heizkreis 1 Soll-Raumtemperatur (Tag)"
    )

    heat_circuit_target_temperature_night_1: State | None = hass.states.get(
        "number.keba_keenergy_12345678_heat_circuit_target_temperature_night_1",
    )
    assert isinstance(heat_circuit_target_temperature_night_1, State)
    assert (
        heat_circuit_target_temperature_night_1.attributes[ATTR_FRIENDLY_NAME]
        == "Heizkreis 1 Soll-Raumtemperatur (Nacht)"
    )


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
        (
            "number.keba_keenergy_12345678_heat_pump_compressor_night_speed",
            50,
            '[{"name": "APPL.CtrlAppl.sParam.heatpump[0].HeatPumpPowerCtrl.param.maxPowerScaledNight", "value": "0.5"}]',  # noqa: E501
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
    """Test set the value."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
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
    """Test set the value out of range."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
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
    """Test set the value without required attribute."""
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
        # Read API after services call
        MULTIPLE_POSITIONS_RESPONSE,
        get_multi_positions_data_response(),
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
