"""Support for the KEBA KeEnergy climate."""

import logging
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from typing import Any
from typing import Final
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate import ClimateEntityDescription
from homeassistant.components.climate.const import ClimateEntityFeature
from homeassistant.components.climate.const import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.climate.const import HVACAction
from homeassistant.components.climate.const import HVACMode
from homeassistant.components.climate.const import PRESET_AWAY
from homeassistant.components.climate.const import PRESET_BOOST
from homeassistant.components.climate.const import PRESET_COMFORT
from homeassistant.components.climate.const import PRESET_HOME
from homeassistant.components.climate.const import PRESET_SLEEP
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.const import STATE_ON
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HassJob
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatCircuitHeatRequest
from keba_keenergy_api.constants import HeatCircuitOperatingMode
from keba_keenergy_api.constants import SectionPrefix

from .const import ATTR_OFFSET
from .const import DOMAIN
from .const import FLASH_WRITE_DELAY
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyEntity

if TYPE_CHECKING:
    from zoneinfo import ZoneInfo

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES: Final[int] = 0

HEAT_CIRCUIT_PRESET_TO_HA: Final[dict[int, str]] = {
    HeatCircuitOperatingMode.AUTO.value: PRESET_HOME,
    HeatCircuitOperatingMode.HOLIDAY.value: PRESET_AWAY,
    HeatCircuitOperatingMode.DAY.value: PRESET_COMFORT,
    HeatCircuitOperatingMode.NIGHT.value: PRESET_SLEEP,
    HeatCircuitOperatingMode.PARTY.value: PRESET_BOOST,
}

HEAT_CIRCUIT_HVAC_ACTION_TO_HA: Final[dict[int, HVACAction]] = {
    HeatCircuitHeatRequest.OFF.value: HVACAction.IDLE,
    HeatCircuitHeatRequest.ON.value: HVACAction.HEATING,
    HeatCircuitHeatRequest.FLOW_OFF.value: HVACAction.IDLE,
    HeatCircuitHeatRequest.TEMPORARY_OFF.value: HVACAction.IDLE,
    HeatCircuitHeatRequest.ROOM_OFF.value: HVACAction.IDLE,
    HeatCircuitHeatRequest.OUTDOOR_OFF.value: HVACAction.IDLE,
    HeatCircuitHeatRequest.INFLOW_OFF.value: HVACAction.IDLE,
}

TEMPERATURE_OFFSET_SCHEMA = {
    vol.Required(ATTR_OFFSET, default=0): vol.Coerce(float),
}

TEMPERATURE_SCHEMA = {
    vol.Required(ATTR_TEMPERATURE): vol.Coerce(float),
}


class KebaKeEnergyClimateEntity(KebaKeEnergyEntity, ClimateEntity):
    """KEBA KeEnergy climate entity."""

    _attr_supported_features: ClimateEntityFeature = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )

    _attr_hvac_modes: list[HVACMode] = [  # noqa: RUF012
        HVACMode.AUTO,
        HVACMode.HEAT,
        HVACMode.OFF,
    ]
    _attr_preset_modes: list[str] = list(HEAT_CIRCUIT_PRESET_TO_HA.values())  # noqa: RUF012

    _attr_target_temperature_step: float = 0.5
    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS
    _attr_name = None

    _enable_turn_on_off_backwards_compatibility = False

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: ClimateEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize KEBA KeEnergy climate entity."""
        self.entity_description = description

        super().__init__(coordinator, entry, section_id, index)

        self.entity_id = f"{CLIMATE_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

        self._operating_mode_status: int | None = None

        self._pending_key = "target_temperature_offset"
        self._pending_section = HeatCircuit.TARGET_TEMPERATURE_OFFSET
        self._pending_device_numbers = self.coordinator.heat_circuit_numbers

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        return "mdi:hvac" if self.hvac_mode == HVACMode.HEAT else "mdi:hvac-off"

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return (
            self.get_value("room_temperature", expected_type=float)
            if self.coordinator.has_room_temperature(index=self.index or 0) == STATE_ON
            else None
        )

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        target_temperature: float | None = None
        selected_target_temperature: float | None = self.get_value("selected_target_temperature", expected_type=float)
        target_temperature_offset: float | None

        if self._pending_value is not None and self._async_call_later:
            target_temperature_offset = self._pending_value
        else:
            target_temperature_offset = self.get_value("target_temperature_offset", expected_type=float)

        if selected_target_temperature is not None and target_temperature_offset is not None:
            target_temperature = selected_target_temperature + target_temperature_offset

        return target_temperature

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        selected_target_temperature: float | None = self.get_value("selected_target_temperature", expected_type=float)
        target_temperature_offset: float = float(
            self.get_attribute("target_temperature_offset", attr="lower_limit"),
        )

        assert selected_target_temperature is not None
        return selected_target_temperature + target_temperature_offset

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        selected_target_temperature: float | None = self.get_value("selected_target_temperature", expected_type=float)
        target_temperature_offset: float = float(
            self.get_attribute("target_temperature_offset", attr="upper_limit"),
        )

        assert selected_target_temperature is not None
        return selected_target_temperature + target_temperature_offset

    @property
    def current_humidity(self) -> float | None:
        """Return the current humidity."""
        return (
            self.get_value("room_humidity", expected_type=float)
            if self.coordinator.has_room_humidity(index=self.index or 0) == STATE_ON
            else None
        )

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation."""
        hvac_mode: HVACMode | None = None
        operating_mode: str | None = self.get_value("operating_mode", expected_type=str)

        if operating_mode:
            if HeatCircuitOperatingMode[operating_mode.upper()].value == HeatCircuitOperatingMode.AUTO.value:
                hvac_mode = HVACMode.AUTO
            elif HeatCircuitOperatingMode[operating_mode.upper()].value in [
                HeatCircuitOperatingMode.HOLIDAY.value,
                HeatCircuitOperatingMode.DAY.value,
                HeatCircuitOperatingMode.NIGHT.value,
                HeatCircuitOperatingMode.PARTY.value,
            ]:
                hvac_mode = HVACMode.HEAT
            else:
                hvac_mode = HVACMode.OFF

        return hvac_mode

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation if supported."""
        hvac_action: HVACAction | None = None

        if self.hvac_mode == HVACMode.OFF:
            hvac_action = HVACAction.OFF
        else:
            heat_request: str | None = self.get_value("heat_request", expected_type=str)

            if heat_request:
                hvac_action = HEAT_CIRCUIT_HVAC_ACTION_TO_HA[HeatCircuitHeatRequest[heat_request.upper()].value]

        return hvac_action

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        preset_mode: str = PRESET_HOME
        operating_mode: str | None = self.get_value("operating_mode", expected_type=str)

        if (
            operating_mode
            and HeatCircuitOperatingMode[operating_mode.upper()].value != HeatCircuitOperatingMode.OFF.value
        ):
            preset_mode = HEAT_CIRCUIT_PRESET_TO_HA[HeatCircuitOperatingMode[operating_mode.upper()].value]

        return preset_mode

    async def async_turn_off(self) -> None:
        """Turn off the heat circuit."""
        await self.async_set_hvac_mode(hvac_mode=HVACMode.OFF)

    async def async_turn_on(self) -> None:
        """Turn on the heat circuit."""
        await self.async_set_hvac_mode(hvac_mode=HVACMode.AUTO)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set hvac mode for heat circuit."""
        operating_mode_status: int | None = None

        if hvac_mode == HVACMode.AUTO:
            operating_mode_status = HeatCircuitOperatingMode.AUTO.value
            await self._async_set_away_date_range(PRESET_HOME)
            self._attr_preset_mode = PRESET_HOME
        elif hvac_mode == HVACMode.HEAT:
            operating_mode_status = HeatCircuitOperatingMode.DAY.value
        elif hvac_mode == HVACMode.OFF:
            operating_mode_status = HeatCircuitOperatingMode.OFF.value

        if operating_mode_status is not None and self._operating_mode_status != operating_mode_status:
            self._operating_mode_status = operating_mode_status

            await self._async_write_data(
                operating_mode_status,
                section=HeatCircuit.OPERATING_MODE,
                device_numbers=self.coordinator.heat_circuit_numbers,
            )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode for heat circuit."""
        await self._async_set_away_date_range(preset_mode)

        for key, value in HEAT_CIRCUIT_PRESET_TO_HA.items():
            if value == preset_mode and preset_mode not in (self.preset_mode, PRESET_AWAY):
                await self._async_write_data(
                    key,
                    section=HeatCircuit.OPERATING_MODE,
                    device_numbers=self.coordinator.heat_circuit_numbers,
                )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if temperature := kwargs.get(ATTR_TEMPERATURE):
            self._pending_value = temperature - self.get_value("selected_target_temperature", expected_type=float)

            if self._async_call_later:
                self._async_call_later()
                self._async_call_later = None

            self._async_call_later = async_call_later(
                hass=self.hass,
                delay=FLASH_WRITE_DELAY,
                action=HassJob(
                    self._async_debounced_write_data,
                    cancel_on_shutdown=True,
                ),
            )

    async def _async_set_away_date_range(self, preset_mode: str, /) -> None:
        tz: ZoneInfo = await self.coordinator.get_timezone()
        now: date = dt_util.now(tz).date()
        start_date_tz: datetime = datetime.combine(now, time.min, tzinfo=tz)
        end_date_tz: datetime = datetime.combine(now, time.max, tzinfo=tz)

        if preset_mode == PRESET_AWAY:
            await self.coordinator.set_away_date_range(
                start_timestamp=start_date_tz.timestamp(),
                end_timestamp=(end_date_tz + timedelta(days=365)).timestamp(),
            )
        elif self.preset_mode == PRESET_AWAY and preset_mode != PRESET_AWAY:
            await self.coordinator.set_away_date_range(
                start_timestamp=(start_date_tz - timedelta(days=1)).timestamp(),
                end_timestamp=(end_date_tz - timedelta(days=1)).timestamp(),
            )


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy climates from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data
    climates: list[KebaKeEnergyClimateEntity] = [
        KebaKeEnergyClimateEntity(
            coordinator,
            description=ClimateEntityDescription(
                key="heat_circuit",
                translation_key="heat_circuit",
            ),
            entry=entry,
            section_id=SectionPrefix.HEAT_CIRCUIT.value,
            index=index if coordinator.heat_circuit_numbers > 1 else None,
        )
        for index in range(coordinator.heat_circuit_numbers)
    ]

    async_add_entities(climates)
