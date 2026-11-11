# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the climate entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from homeassistant.components.climate.const import ATTR_CURRENT_HUMIDITY
from homeassistant.components.climate.const import ATTR_CURRENT_TEMPERATURE
from homeassistant.components.climate.const import ATTR_HVAC_ACTION
from homeassistant.components.climate.const import ATTR_HVAC_MODE
from homeassistant.components.climate.const import ATTR_HVAC_MODES
from homeassistant.components.climate.const import ATTR_MAX_TEMP
from homeassistant.components.climate.const import ATTR_MIN_TEMP
from homeassistant.components.climate.const import ATTR_PRESET_MODE
from homeassistant.components.climate.const import ATTR_PRESET_MODES
from homeassistant.components.climate.const import DEFAULT_MAX_TEMP
from homeassistant.components.climate.const import DEFAULT_MIN_TEMP
from homeassistant.components.climate.const import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.climate.const import PRESET_AWAY
from homeassistant.components.climate.const import PRESET_BOOST
from homeassistant.components.climate.const import PRESET_COMFORT
from homeassistant.components.climate.const import PRESET_HOME
from homeassistant.components.climate.const import PRESET_SLEEP
from homeassistant.components.climate.const import SERVICE_SET_HVAC_MODE
from homeassistant.components.climate.const import SERVICE_SET_PRESET_MODE
from homeassistant.components.climate.const import HVACAction
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import Platform
from homeassistant.exceptions import HomeAssistantError
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_component import async_update_entity
from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import HeatingCircuitRequest
from keba_keenergy_api.enums import HeatingCircuitType
from keba_keenergy_api.enums import HeatPumpState
from pytest_homeassistant.common import snapshot_platform

from tests import fire_debounced_writes
from tests import get_state
from tests import replace_attributes
from tests import replace_values
from tests import set_target_temperature
from tests.const import HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET
from tests.const import NOW
from tests.const import OTHER_MODES_VALUES
from tests.const import Response
from tests.test_climate_data import AUTO_VALUES
from tests.test_climate_data import AWAY_DATE_RANGE_RESET_WRITE
from tests.test_climate_data import AWAY_DATE_RANGE_VALUES
from tests.test_climate_data import AWAY_PRESET_WRITE
from tests.test_climate_data import COOLING_SCHEDULE_VALUES
from tests.test_climate_data import COOLING_VALUES
from tests.test_climate_data import HEAT_CIRCUIT_1_ENTITY_ID
from tests.test_climate_data import HEAT_CIRCUIT_ENTITY_ID
from tests.test_climate_data import HEAT_CIRCUIT_MODE
from tests.test_climate_data import NIGHT
from tests.test_climate_data import NIGHT_TEMPERATURE_VALUES
from tests.test_climate_data import OFF_VALUES
from tests.test_climate_data import PARTY_VALUES
from tests.test_climate_data import REDUCED_VALUES
from tests.test_climate_data import SELECTED_TARGET_TEMPERATURE
from tests.test_climate_data import TARGET_TEMPERATURE_WITH_OFFSET
from tests.test_climate_data import get_hvac_action_values
from tests.test_climate_data import get_operating_mode_write

if TYPE_CHECKING:
    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
    from homeassistant.helpers import entity_registry as er
    from pytest_homeassistant.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI
    from tests.const import Attributes

pytestmark = pytest.mark.freeze_time(NOW)


@pytest.mark.parametrize("language", ["de", "en"], ids=["de", "en"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_climate(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
    language: str,
) -> None:
    """Test the states of all climate entities."""
    hass.config.language = language
    fake_api.load_device("multiple_devices")
    fake_api.platforms = [Platform.CLIMATE]
    await fake_api.setup_integration()

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.parametrize(
    ("circuit_type", "expected_modes"),
    [
        (
            HeatingCircuitType.HEATING,
            (
                [HVACMode.AUTO, HVACMode.HEAT, HVACMode.OFF],
                [PRESET_HOME, PRESET_AWAY, PRESET_COMFORT, PRESET_SLEEP, PRESET_BOOST],
            ),
        ),
        (
            HeatingCircuitType.COOLING,
            (
                [HVACMode.AUTO, HVACMode.COOL, HVACMode.OFF],
                [PRESET_HOME, PRESET_COMFORT, PRESET_SLEEP, PRESET_BOOST],
            ),
        ),
        (
            HeatingCircuitType.HEATING_AND_COOLING,
            (
                [HVACMode.AUTO, HVACMode.HEAT_COOL, HVACMode.OFF],
                [PRESET_HOME, PRESET_AWAY, PRESET_COMFORT, PRESET_SLEEP, PRESET_BOOST],
            ),
        ),
    ],
    ids=["heating", "cooling", "heating_and_cooling"],
)
async def test_hvac_and_preset_modes(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    circuit_type: HeatingCircuitType,
    expected_modes: tuple[list[HVACMode], list[str]],
) -> None:
    """Test that the HVAC modes and presets depend on the type of the heating circuit, only cooling has no away."""
    fake_api.load_device("single_device")
    fake_api.fixed_data = replace_values(fake_api.fixed_data, {HEAT_CIRCUIT_MODE: str(circuit_type.value)})
    fake_api.data = replace_values(fake_api.data, REDUCED_VALUES)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)

    assert (state.attributes[ATTR_HVAC_MODES], state.attributes[ATTR_PRESET_MODES]) == expected_modes


async def test_set_hvac_mode_cool(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the HVAC mode cool of a heating circuit that only cools writes the operating mode normal."""
    fake_api.load_device("single_device")
    fake_api.fixed_data = replace_values(fake_api.fixed_data, COOLING_VALUES)
    fake_api.data = replace_values(fake_api.data, OFF_VALUES)
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_HVAC_MODE,
        service_data={
            ATTR_ENTITY_ID: HEAT_CIRCUIT_ENTITY_ID,
            ATTR_HVAC_MODE: HVACMode.COOL,
        },
        blocking=True,
    )

    assert fake_api.write_requests() == [get_operating_mode_write(HeatingCircuitOperatingMode.NORMAL)]


async def test_set_preset_mode_away_of_cooling_circuit(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a heating circuit that only cools rejects the away preset."""
    fake_api.load_device("single_device")
    fake_api.fixed_data = replace_values(fake_api.fixed_data, COOLING_VALUES)
    fake_api.data = replace_values(fake_api.data, REDUCED_VALUES)
    await fake_api.setup_integration()

    with pytest.raises(ServiceValidationError) as error:
        await hass.services.async_call(
            domain=CLIMATE_DOMAIN,
            service=SERVICE_SET_PRESET_MODE,
            service_data={
                ATTR_ENTITY_ID: HEAT_CIRCUIT_ENTITY_ID,
                ATTR_PRESET_MODE: PRESET_AWAY,
            },
            blocking=True,
        )

    assert error.value.translation_key == "not_valid_preset_mode"
    assert fake_api.write_requests() == []


@pytest.mark.parametrize(
    ("offset_attributes", "expected_limits"),
    [
        # The selected target temperature 20.0 plus the limits of the offset (-2.5 and 2.5).
        ({"upperLimit": "2.5", "lowerLimit": "-2.5"}, (17.5, 22.5)),
        ({}, (DEFAULT_MIN_TEMP, DEFAULT_MAX_TEMP)),
    ],
    ids=["offset_limits", "without_limits"],
)
async def test_temperature_limits(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    offset_attributes: Attributes,
    expected_limits: tuple[float, float],
) -> None:
    """Test the limits of the target temperature, the defaults of Home Assistant without the limits of the offset."""
    fake_api.load_device("single_device")
    fake_api.data = replace_attributes(fake_api.data, HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET, offset_attributes)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)

    assert (state.attributes[ATTR_MIN_TEMP], state.attributes[ATTR_MAX_TEMP]) == expected_limits


async def test_set_temperature_out_of_range(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a target temperature outside of the limits is rejected and not written."""
    fake_api.load_device("single_device")
    await fake_api.setup_integration()

    with pytest.raises(ServiceValidationError) as error:
        await set_target_temperature(hass, HEAT_CIRCUIT_ENTITY_ID, 23.0)

    await fire_debounced_writes(hass, freezer)

    assert error.value.translation_key == "temp_out_of_range"
    assert fake_api.write_requests() == []


async def test_target_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the target temperature is the selected target temperature 20.0 plus the offset 1.5."""
    fake_api.load_device("single_device")
    fake_api.data = replace_values(fake_api.data, {HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET: "1.5"})
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == TARGET_TEMPERATURE_WITH_OFFSET


async def test_set_temperature_debounced(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that quick target temperature changes are shown at once and written once, with the last value."""
    fake_api.load_device("single_device")
    fake_api.responses = fake_api.setup_responses(
        replace_values(fake_api.data, {HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET: "1.5"}),
        # Read the API after the update of the entity.
        replace_values(fake_api.data, {HEAT_CIRCUIT_TARGET_TEMPERATURE_OFFSET: "1.5"}),
    )
    await fake_api.setup_integration()

    temperatures: tuple[float, ...] = (21.0, 20.5)

    for temperature in temperatures:
        await set_target_temperature(hass, HEAT_CIRCUIT_ENTITY_ID, temperature)

    await async_update_entity(hass, HEAT_CIRCUIT_ENTITY_ID)

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == temperatures[-1]
    assert fake_api.write_requests() == []

    await fire_debounced_writes(hass, freezer)

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp", "value": "0.5"}]',
    ]


async def test_target_temperature_without_selected_target_temperature(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the day temperature 20.5 of the operating mode is the base if there is no selected temperature."""
    fake_api.load_device("multiple_devices")
    fake_api.unsupported_variables = {"APPL.CtrlAppl.sParam.heatCircuit[0].values.selectedSetTemp"}
    await fake_api.setup_integration()

    temperature: float = 21.0
    await set_target_temperature(hass, HEAT_CIRCUIT_1_ENTITY_ID, temperature)

    await fire_debounced_writes(hass, freezer)

    assert get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID).attributes[ATTR_TEMPERATURE] == temperature
    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp", "value": "0.5"}]',
    ]


async def test_set_temperature_without_target_temperature(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that no offset is written if the schedule has no time zone and no selected target temperature."""
    fake_api.load_device("multiple_devices")
    fake_api.timezone["timezone"] = "Invalid/Zone"
    fake_api.unsupported_variables = {"APPL.CtrlAppl.sParam.heatCircuit[0].values.selectedSetTemp"}
    fake_api.data = replace_values(fake_api.data, AUTO_VALUES)
    await fake_api.setup_integration()

    await set_target_temperature(hass, HEAT_CIRCUIT_1_ENTITY_ID, 21.0)

    await fire_debounced_writes(hass, freezer)

    assert get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID).attributes[ATTR_TEMPERATURE] is None
    assert fake_api.write_requests() == []


@pytest.mark.parametrize(
    "expected_temperature",
    [22.0, pytest.param(21.5, marks=pytest.mark.freeze_time(NIGHT))],
    ids=["day", "night"],
)
async def test_target_temperature_of_schedule(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    expected_temperature: float,
) -> None:
    """Test that the schedule uses the day temperature 20.5 or the night temperature 20.0 plus the offset 1.5."""
    fake_api.load_device("multiple_devices")
    fake_api.data = replace_values(fake_api.data, AUTO_VALUES)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == expected_temperature


async def test_target_temperature_of_schedule_with_invalid_time_zone(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the schedule uses the selected target temperature 20.0 plus the offset 1.5 without a time zone."""
    fake_api.load_device("multiple_devices")
    fake_api.timezone["timezone"] = "Invalid/Zone"
    fake_api.data = replace_values(fake_api.data, AUTO_VALUES)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == TARGET_TEMPERATURE_WITH_OFFSET


@pytest.mark.parametrize(
    ("week_timer_without_day_block", "expected_temperature"),
    [(None, 25.0), ("weekTimerCool", 24.0)],
    ids=["day", "night"],
)
async def test_target_temperature_of_schedule_of_cooling_circuit(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    week_timer_without_day_block: str | None,
    expected_temperature: float,
) -> None:
    """Test that a heating circuit that only cools uses the cooling timer and the cooling temperatures 25.0 and 24.0.

    The heating timer has day, so the cooling timer without a day block is night.
    """
    fake_api.load_device("single_device")
    fake_api.week_timer_without_day_block = week_timer_without_day_block
    fake_api.fixed_data = replace_values(fake_api.fixed_data, COOLING_VALUES)
    fake_api.data = replace_values(fake_api.data, COOLING_SCHEDULE_VALUES)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == expected_temperature


async def test_target_temperature_of_schedule_of_heating_and_cooling_circuit(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a heating circuit that heats and cools keeps the selected target temperature 20.0 of the control unit.

    Only the control unit knows if it is the season of heating or cooling.
    """
    fake_api.load_device("single_device")
    fake_api.fixed_data = replace_values(
        fake_api.fixed_data,
        {HEAT_CIRCUIT_MODE: str(HeatingCircuitType.HEATING_AND_COOLING.value)},
    )
    fake_api.data = replace_values(fake_api.data, AUTO_VALUES)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == SELECTED_TARGET_TEMPERATURE


async def test_set_preset_mode_shows_target_temperature_of_mode(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the night temperature 19.5 plus the offset 1.5 is shown, not the selected target temperature 20.0."""
    fake_api.load_device("multiple_devices")
    fake_api.responses = fake_api.setup_responses(
        replace_values(fake_api.data, NIGHT_TEMPERATURE_VALUES),
        replace_values(fake_api.data, {**REDUCED_VALUES, **NIGHT_TEMPERATURE_VALUES}),
    )
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID, ATTR_PRESET_MODE: PRESET_SLEEP},
        blocking=True,
    )

    expected: tuple[str, float] = (PRESET_SLEEP, 21.0)
    state: State = get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID)
    assert (state.attributes[ATTR_PRESET_MODE], state.attributes[ATTR_TEMPERATURE]) == expected
    await hass.async_block_till_done()
    assert get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID).attributes[ATTR_TEMPERATURE] == expected[1]


async def test_set_preset_mode_discards_pending_temperature(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a pending offset of the previous mode is not written after a preset change."""
    fake_api.load_device("multiple_devices")
    fake_api.responses = fake_api.setup_responses(fake_api.data, replace_values(fake_api.data, REDUCED_VALUES))
    await fake_api.setup_integration()

    await set_target_temperature(hass, HEAT_CIRCUIT_1_ENTITY_ID, 22.0)
    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID, ATTR_PRESET_MODE: PRESET_SLEEP},
        blocking=True,
    )
    await fire_debounced_writes(hass, freezer)

    assert fake_api.write_requests() == [get_operating_mode_write(HeatingCircuitOperatingMode.REDUCED)]


@pytest.mark.parametrize(
    ("values", "expected_writes"),
    [
        (AUTO_VALUES, [AWAY_PRESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.NORMAL)]),
        (OFF_VALUES, [AWAY_PRESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.NORMAL)]),
        (REDUCED_VALUES, [AWAY_PRESET_WRITE]),
        (PARTY_VALUES, [AWAY_PRESET_WRITE]),
    ],
    ids=["auto", "off", "reduced", "party"],
)
async def test_set_preset_mode_away_heats(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    values: dict[str, str],
    expected_writes: list[str],
) -> None:
    """Test that away sets the HVAC mode heat, a circuit that is not in a manual operating mode gets day."""
    fake_api.load_device("multiple_devices")
    fake_api.data = replace_values(fake_api.data, values)
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID, ATTR_PRESET_MODE: PRESET_AWAY},
        blocking=True,
    )

    state: State = get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID)
    assert (state.state, state.attributes[ATTR_PRESET_MODE]) == (HVACMode.HEAT, PRESET_AWAY)
    assert fake_api.write_requests() == expected_writes


async def test_set_preset_mode_ends_away_with_unchanged_operating_mode(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the end of away only resets the date range if the operating mode below it is the new one."""
    fake_api.load_device("multiple_devices")
    away_data_response: Response = replace_values(fake_api.data, AWAY_DATE_RANGE_VALUES)
    fake_api.data = away_data_response
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID, ATTR_PRESET_MODE: PRESET_COMFORT},
        blocking=True,
    )

    assert fake_api.write_requests() == [AWAY_DATE_RANGE_RESET_WRITE]


async def test_set_preset_mode_away_while_away(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the away preset is not written again while it is active."""
    fake_api.load_device("multiple_devices")
    fake_api.data = replace_values(fake_api.data, OTHER_MODES_VALUES)
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID, ATTR_PRESET_MODE: PRESET_AWAY},
        blocking=True,
    )

    assert fake_api.write_requests() == []


@pytest.mark.parametrize(
    ("service_call", "values", "expected_writes"),
    [
        (
            (SERVICE_TURN_OFF, {}),
            {},
            [get_operating_mode_write(HeatingCircuitOperatingMode.OFF)],
        ),
        (
            (SERVICE_TURN_ON, {}),
            {},
            [get_operating_mode_write(HeatingCircuitOperatingMode.AUTO)],
        ),
        ((SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}), {}, []),
        ((SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}), REDUCED_VALUES, []),
        ((SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}), PARTY_VALUES, []),
        (
            (SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.AUTO}),
            OTHER_MODES_VALUES,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.AUTO)],
        ),
        (
            (SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.HEAT}),
            OTHER_MODES_VALUES,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.NORMAL)],
        ),
        (
            (SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.OFF}),
            OTHER_MODES_VALUES,
            [AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.OFF)],
        ),
    ],
    ids=[
        "turn_off",
        "turn_on",
        "unchanged",
        "heat_while_reduced",
        "heat_while_party",
        "auto_while_away",
        "heat_while_away",
        "off_while_away",
    ],
)
async def test_set_hvac_mode(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    service_call: tuple[str, dict[str, HVACMode]],
    values: dict[str, str],
    expected_writes: list[str],
) -> None:
    """Test setting the HVAC mode of a heating circuit, only a change is written.

    An HVAC mode that is already active keeps the preset, every HVAC mode ends the away date range.
    """
    fake_api.load_device("multiple_devices")
    fake_api.data = replace_values(fake_api.data, values)
    await fake_api.setup_integration()

    service, service_data = service_call
    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=service,
        service_data={ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID, **service_data},
        blocking=True,
    )

    assert fake_api.write_requests() == expected_writes


@pytest.mark.parametrize(
    ("preset_mode", "values", "expected"),
    [
        (
            PRESET_HOME,
            {},
            ([get_operating_mode_write(HeatingCircuitOperatingMode.AUTO)], 0),
        ),
        (PRESET_COMFORT, {}, ([], 0)),
        (
            PRESET_SLEEP,
            {},
            ([get_operating_mode_write(HeatingCircuitOperatingMode.REDUCED)], 0),
        ),
        (
            PRESET_BOOST,
            {},
            ([get_operating_mode_write(HeatingCircuitOperatingMode.PARTY)], 0),
        ),
        (PRESET_AWAY, {}, ([AWAY_PRESET_WRITE], 1)),
        (
            PRESET_HOME,
            OTHER_MODES_VALUES,
            ([AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.AUTO)], 1),
        ),
        (
            PRESET_COMFORT,
            OTHER_MODES_VALUES,
            ([AWAY_DATE_RANGE_RESET_WRITE, get_operating_mode_write(HeatingCircuitOperatingMode.NORMAL)], 1),
        ),
    ],
    ids=["home", "comfort_unchanged", "sleep", "boost", "away", "home_while_away", "comfort_while_away"],
)
async def test_set_preset_mode(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    preset_mode: str,
    values: dict[str, str],
    expected: tuple[list[str], int],
) -> None:
    """Test setting the preset mode of a heating circuit.

    The away preset sets an away date range of one year, leaving it resets the date range to yesterday. Only a
    change of the away date range requests the time zone of the Web HMI (the second expected value).
    """
    fake_api.load_device("multiple_devices")
    fake_api.data = replace_values(fake_api.data, values)
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={
            ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID,
            ATTR_PRESET_MODE: preset_mode,
        },
        blocking=True,
    )

    assert (fake_api.write_requests(), fake_api.time_zone_request_count()) == expected


@pytest.mark.parametrize(
    ("preset_mode", "values", "expected_preset_mode"),
    [
        (PRESET_HOME, (OTHER_MODES_VALUES, {}), PRESET_COMFORT),
    ],
    ids=["home_while_away"],
)
async def test_set_preset_mode_refreshes_target_temperature(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    preset_mode: str,
    values: tuple[dict[str, str], dict[str, str]],
    expected_preset_mode: str,
) -> None:
    """Test that a preset change reads the values again, the control unit knows the target temperature of the mode."""
    fake_api.load_device("multiple_devices")
    fake_api.responses = fake_api.setup_responses(
        replace_values(fake_api.data, values[0]),
        replace_values(fake_api.data, values[1]),
    )
    await fake_api.setup_integration()
    read_count: int = len(fake_api.read_requests())

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={
            ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID,
            ATTR_PRESET_MODE: preset_mode,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    assert len(fake_api.read_requests()) == read_count + 1
    assert get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID).attributes[ATTR_PRESET_MODE] == expected_preset_mode


async def test_set_preset_mode_away_keeps_preset_until_operating_mode_changes(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the away preset stays while the control unit still reports the old operating mode."""
    fake_api.load_device("multiple_devices")
    away_data_response: Response = replace_values(fake_api.data, AWAY_DATE_RANGE_VALUES)
    fake_api.responses = fake_api.setup_responses(fake_api.data, away_data_response)
    await fake_api.setup_integration()

    await hass.services.async_call(
        domain=CLIMATE_DOMAIN,
        service=SERVICE_SET_PRESET_MODE,
        service_data={ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID, ATTR_PRESET_MODE: PRESET_AWAY},
        blocking=True,
    )
    state: State = get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID)
    assert (state.attributes[ATTR_PRESET_MODE], state.attributes[ATTR_TEMPERATURE]) == (PRESET_AWAY, 19.5)

    await async_update_entity(hass, HEAT_CIRCUIT_1_ENTITY_ID)

    state = get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID)
    assert (state.state, state.attributes[ATTR_PRESET_MODE], state.attributes[ATTR_TEMPERATURE]) == (
        HVACMode.HEAT,
        PRESET_AWAY,
        19.5,
    )


async def test_set_preset_mode_away_with_invalid_time_zone(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that an invalid time zone of the Web HMI raises a translated error and writes nothing."""
    fake_api.load_device("multiple_devices")
    fake_api.timezone["timezone"] = "Invalid/Zone"
    await fake_api.setup_integration()

    with pytest.raises(HomeAssistantError) as error:
        await hass.services.async_call(
            domain=CLIMATE_DOMAIN,
            service=SERVICE_SET_PRESET_MODE,
            service_data={
                ATTR_ENTITY_ID: HEAT_CIRCUIT_1_ENTITY_ID,
                ATTR_PRESET_MODE: PRESET_AWAY,
            },
            blocking=True,
        )

    assert error.value.translation_key == "invalid_time_zone"
    assert error.value.translation_placeholders == {"time_zone": "Invalid/Zone"}
    assert fake_api.write_requests() == []


@pytest.mark.usefixtures("init_integration")
async def test_set_temperature(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test setting the target temperature of a heating circuit."""
    await set_target_temperature(hass, HEAT_CIRCUIT_1_ENTITY_ID, 19.5)

    await fire_debounced_writes(hass, freezer)

    assert fake_api.write_requests() == [
        '[{"name": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp", "value": "-1.0"}]'
    ]


@pytest.mark.parametrize(
    "operating_mode",
    [HeatingCircuitOperatingMode.EXTERNAL, HeatingCircuitOperatingMode.ROOM_CONTROL],
    ids=["external", "room_control"],
)
async def test_operating_mode_without_preset(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    operating_mode: HeatingCircuitOperatingMode,
) -> None:
    """Test that a heating circuit in an operating mode without a preset has no preset."""
    fake_api.load_device("single_device")
    fake_api.data = replace_values(
        fake_api.data, {"APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode": str(operating_mode.value)}
    )
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
    assert state.state == HVACMode.OFF
    assert state.attributes[ATTR_PRESET_MODE] is None


async def test_room_sensor_not_in_use(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that the climate entity has no current temperature if the room sensor is not in use (message id not 0).

    The climate entity stays available, the room humidity sensor is still in use.
    """
    fake_api.load_device("multiple_devices")
    fake_api.message_ids = {"APPL.CtrlAppl.sParam.heatCircuit[0].tempRoom.state.msgId": 10}
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_1_ENTITY_ID)
    assert (state.state, state.attributes[ATTR_CURRENT_TEMPERATURE], state.attributes[ATTR_CURRENT_HUMIDITY]) == (
        HVACMode.HEAT,
        None,
        53.0,
    )


@pytest.mark.parametrize(
    ("values", "expected_hvac_action"),
    [
        (get_hvac_action_values(heat_pump_state=HeatPumpState.STANDBY), HVACAction.IDLE),
        (get_hvac_action_values(heat_pump_state=HeatPumpState.PRE_RUN), HVACAction.PREHEATING),
        (get_hvac_action_values(heat_pump_state=HeatPumpState.AUTOMATIC), HVACAction.HEATING),
        (get_hvac_action_values(heat_pump_state=HeatPumpState.DEFROST), HVACAction.DEFROSTING),
        (get_hvac_action_values(heat_pump_state=HeatPumpState.COOLING), HVACAction.IDLE),
        (get_hvac_action_values(heat_pump_state=HeatPumpState.POST_RUN), HVACAction.HEATING),
        (get_hvac_action_values(heat_pump_state=HeatPumpState.PUMP_DOWN), HVACAction.IDLE),
        (get_hvac_action_values(heat_pump_state=HeatPumpState.SHUTDOWN), HVACAction.IDLE),
        (get_hvac_action_values(heat_pump_state=HeatPumpState.ERROR), HVACAction.IDLE),
        (get_hvac_action_values(heat_pump_state=HeatPumpState.SOURCE_FLUSH), HVACAction.IDLE),
        # The heat request of the heating circuit is temporarily off while the heat pump heats the hot water.
        (
            get_hvac_action_values(
                heat_pump_state=HeatPumpState.AUTOMATIC,
                heat_request=HeatingCircuitRequest.TEMPERATURE_PRIORITY_OFF,
            ),
            HVACAction.IDLE,
        ),
        # The heat pump stays in standby with passive cooling.
        (
            get_hvac_action_values(
                heat_pump_state=HeatPumpState.STANDBY,
                heat_request=HeatingCircuitRequest.OFF,
                cool_request=HeatingCircuitRequest.ACTIVE,
            ),
            HVACAction.COOLING,
        ),
        (
            get_hvac_action_values(
                heat_pump_state=HeatPumpState.STANDBY,
                heat_request=HeatingCircuitRequest.OFF,
                cool_request=HeatingCircuitRequest.OUTDOOR_OFF,
            ),
            HVACAction.IDLE,
        ),
        (
            get_hvac_action_values(
                heat_pump_state=HeatPumpState.AUTOMATIC,
                operating_mode=HeatingCircuitOperatingMode.OFF,
            ),
            HVACAction.OFF,
        ),
    ],
    ids=[
        "standby",
        "pre_run",
        "automatic",
        "defrost",
        "cooling",
        "post_run",
        "pump_down",
        "shutdown",
        "error",
        "source_flush",
        "automatic_hot_water_priority",
        "standby_cool_request",
        "standby_cool_request_outdoor_off",
        "automatic_hvac_mode_off",
    ],
)
async def test_hvac_action(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    values: dict[str, str],
    expected_hvac_action: HVACAction,
) -> None:
    """Test the action of a heating circuit with the requests of the heating circuit and the heat pump state."""
    fake_api.load_device("single_device")
    fake_api.data = replace_values(fake_api.data, values)
    await fake_api.setup_integration()

    state: State = get_state(hass, HEAT_CIRCUIT_ENTITY_ID)
    assert state.attributes[ATTR_HVAC_ACTION] == expected_hvac_action
