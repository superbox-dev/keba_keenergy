# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Tests for the number entities."""

from __future__ import annotations

from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING

import probatio
import pytest
from homeassistant.components.number import ATTR_MAX
from homeassistant.components.number import ATTR_MIN
from homeassistant.components.number import DEFAULT_MAX_VALUE
from homeassistant.components.number import DEFAULT_MIN_VALUE
from homeassistant.const import Platform
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.keba_keenergy.const import FLASH_WRITE_DELAY
from tests import fire_debounced_writes
from tests import get_platform_states
from tests import get_state
from tests import set_number_value
from tests.api_data import MULTIPLE_DEVICES_DATA_RESPONSE
from tests.api_data import Response
from tests.api_data import get_multiple_devices_responses
from tests.api_data import get_single_device_data_response
from tests.api_data import get_single_device_responses
from tests.api_data import update_response
from tests.test_number_data import HEATING_CURVE_SLOPE_ENTITY_ID
from tests.test_number_data import TARGET_TEMPERATURE_OFFSET_ENTITY_ID
from tests.test_number_data import TARGET_TEMPERATURE_OFFSET_WRITE

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.core import State
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from syrupy.assertion import SnapshotAssertion

    from tests.conftest import FakeKebaKeEnergyAPI


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "language")
async def test_numbers(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the states of all number entities."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE, has_passive_cooling="true")
    await fake_api.setup_integration()

    for state in get_platform_states(hass, config_entry, Platform.NUMBER):
        assert state == snapshot(name=state.entity_id)


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
        (
            "number.keba_keenergy_12345678_external_heat_source_min_runtime_excess_energy_1",
            30,
            '[{"name": "APPL.CtrlAppl.sParam.extHeatSource[0].param.minRunTimeExcessEnergy", "value": "1800"}]',
        ),
    ],
    ids=[
        "solar_circuit_target_temperature_1",
        "solar_circuit_target_temperature_2",
        "buffer_tank_standby_temperature",
        "hot_water_tank_standby_temperature",
        "hot_water_tank_target_temperature",
        "heat_circuit_target_temperature_day",
        "heat_circuit_target_temperature_night",
        "heat_circuit_target_temperature_away",
        "heat_circuit_target_temperature_offset",
        "heat_circuit_heating_curve_offset",
        "heat_circuit_heating_curve_slope",
        "external_heat_source_min_runtime_excess_energy",
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_set_value(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: float,
    expected: str,
) -> None:
    """Test setting the value of a number entity."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    await set_number_value(hass, entity_id, value)

    await fire_debounced_writes(hass)

    assert fake_api.write_requests() == [expected]


@pytest.mark.parametrize(
    ("entity_id", "value", "expected"),
    [
        (
            "number.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
            100,
            (
                r"Value 100\.0 for number\.keba_keenergy_12345678_hot_water_tank_target_temperature_1 "
                r"is outside valid range 0\.0 - 52\.0"
            ),
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
            -10,
            (
                r"Value -10\.0 for number\.keba_keenergy_12345678_heat_circuit_target_temperature_day_1 "
                r"is outside valid range 10\.0 - 30\.0"
            ),
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1",
            -3,
            (
                r"Value -3\.0 for number\.keba_keenergy_12345678_heat_circuit_target_temperature_offset_1 "
                r"is outside valid range -2\.5 - 2\.5"
            ),
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_heating_curve_offset_1",
            -11,
            (
                r"Value -11\.0 for number\.keba_keenergy_12345678_heat_circuit_heating_curve_offset_1 "
                r"is outside valid range -10\.0 - 10\.0"
            ),
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_heating_curve_slope_1",
            -0.1,
            (
                r"Value -0\.1 for number\.keba_keenergy_12345678_heat_circuit_heating_curve_slope_1 "
                r"is outside valid range 0\.0 - 5\.0"
            ),
        ),
        (
            "number.keba_keenergy_12345678_external_heat_source_min_runtime_excess_energy_1",
            181,
            (
                r"Value 181\.0 for number\.keba_keenergy_12345678_external_heat_source_min_runtime_excess_energy_1 "
                r"is outside valid range 0\.0 - 180\.0"
            ),
        ),
    ],
    ids=[
        "hot_water_tank_target_temperature",
        "heat_circuit_target_temperature_day",
        "heat_circuit_target_temperature_offset",
        "heat_circuit_heating_curve_offset",
        "heat_circuit_heating_curve_slope",
        "external_heat_source_min_runtime_excess_energy",
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_set_value_out_of_range(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: float,
    expected: str,
) -> None:
    """Test that a number entity rejects a value outside of its limits."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    with pytest.raises(ServiceValidationError, match=expected):
        await set_number_value(hass, entity_id, value)


@pytest.mark.parametrize(
    ("entity_id", "value", "expected"),
    [
        (
            "number.keba_keenergy_12345678_hot_water_tank_target_temperature_1",
            None,
            r"expected float",
        ),
        (
            "number.keba_keenergy_12345678_heat_circuit_target_temperature_day_1",
            "bad",
            r"expected float",
        ),
    ],
    ids=["none", "string"],
)
async def test_set_value_invalid_data(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    value: str | None,
    expected: str,
) -> None:
    """Test that the schema of the action rejects a value that is not a number."""
    fake_api.responses = get_multiple_devices_responses(MULTIPLE_DEVICES_DATA_RESPONSE)
    await fake_api.setup_integration()

    with pytest.raises(probatio.Invalid, match=expected):
        await set_number_value(hass, entity_id, value)


async def test_set_value_debounced(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that quick value changes are shown at once and written once, with the last value."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
        # Read the API after the update of the entity.
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
    )
    await fake_api.setup_integration()

    values: tuple[float, ...] = (1.0, 0.5)

    for value in values:
        await set_number_value(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID, value)

    await async_update_entity(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID)

    state: State = get_state(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID)
    assert state.state == str(values[-1])
    assert fake_api.write_requests() == []

    await fire_debounced_writes(hass)

    assert fake_api.write_requests() == [TARGET_TEMPERATURE_OFFSET_WRITE]


@pytest.mark.parametrize(
    ("entity_id", "response", "value"),
    [
        (
            TARGET_TEMPERATURE_OFFSET_ENTITY_ID,
            get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
            1.5,
        ),
        # The Web HMI returns `0.8` as Float32 (`0.80000001`).
        (
            HEATING_CURVE_SLOPE_ENTITY_ID,
            update_response(
                get_single_device_data_response(),
                "APPL.CtrlAppl.sParam.heatCircuit[0].param.heatCurveGradient",
                value="0.80000001",
            ),
            0.8,
        ),
    ],
    ids=["value", "float32_value"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_set_unchanged_value(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    entity_id: str,
    response: Response,
    value: float,
) -> None:
    """Test that the current value of a number entity is not written again."""
    fake_api.responses = get_single_device_responses(response)
    await fake_api.setup_integration()

    await set_number_value(hass, entity_id, value)

    await fire_debounced_writes(hass)

    assert fake_api.write_requests() == []


async def test_set_value_back_before_write(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a value set back to the current value before the debounced write is not written."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
    )
    await fake_api.setup_integration()

    await set_number_value(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID, 0.5)
    await set_number_value(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID, 1.5)

    await fire_debounced_writes(hass)

    assert get_state(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID).state == "1.5"
    assert fake_api.write_requests() == []


async def test_limits_after_update(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a number entity uses the default limits until an update provides the limits of the API."""
    fake_api.responses = get_single_device_responses(
        update_response(
            get_single_device_data_response(),
            "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp",
            attributes={},
        ),
        get_single_device_data_response(),
    )
    await fake_api.setup_integration()

    state: State = get_state(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID)
    assert (state.attributes[ATTR_MIN], state.attributes[ATTR_MAX]) == (DEFAULT_MIN_VALUE, DEFAULT_MAX_VALUE)

    await config_entry.runtime_data.async_refresh()

    state = get_state(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID)
    assert (state.attributes[ATTR_MIN], state.attributes[ATTR_MAX]) == (-2.5, 2.5)


async def test_debounced_value_not_written_after_unload(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a pending debounced value is not written after the integration was unloaded."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
    )
    await fake_api.setup_integration()

    await set_number_value(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID, 0.5)

    await hass.config_entries.async_unload(config_entry.entry_id)

    await fire_debounced_writes(hass)

    assert fake_api.write_requests() == []


async def test_debounced_write_failed(
    hass: HomeAssistant,
    fake_api: FakeKebaKeEnergyAPI,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that a failed debounced write shows the previous value again and logs a warning, not an error."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
    )
    await fake_api.setup_integration()
    fake_api.write_status = HTTPStatus.BAD_REQUEST

    await set_number_value(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID, 0.5)

    await fire_debounced_writes(hass)

    state: State = get_state(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID)
    assert state.state == "1.5"
    assert fake_api.write_requests() == [TARGET_TEMPERATURE_OFFSET_WRITE]
    # A warning, `fail_on_log_errors` fails the test on an error.
    assert (
        f"Failed to write the value of {TARGET_TEMPERATURE_OFFSET_ENTITY_ID}: "
        "An error occurred while communicating with the API"
    ) in caplog.text


async def test_debounced_write_during_update(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    """Test that a value written during an update is not replaced by the previous value of the update."""
    fake_api.responses = get_single_device_responses(
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
        # The update reads the previous value while the value is written.
        get_single_device_data_response(heat_circuit_target_temperature_offset="1.5"),
        # The update reads the values again after the write.
        get_single_device_data_response(heat_circuit_target_temperature_offset="0.5"),
    )
    await fake_api.setup_integration()

    async def set_value_during_read() -> None:
        await set_number_value(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID, 0.5)
        # Only the timer of the write, waiting for it would wait for the update that is still reading.
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=FLASH_WRITE_DELAY))

    fake_api.during_read = set_value_during_read
    await config_entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    state: State = get_state(hass, TARGET_TEMPERATURE_OFFSET_ENTITY_ID)
    assert state.state == "0.5"
    assert fake_api.write_requests() == [TARGET_TEMPERATURE_OFFSET_WRITE]
