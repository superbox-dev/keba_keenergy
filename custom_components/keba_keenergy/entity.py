"""Entity classes for the KEBA KeEnergy integration."""

import logging
from collections.abc import Mapping
from functools import cached_property
from typing import Any
from typing import TYPE_CHECKING

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from keba_keenergy_api.constants import BufferTank
from keba_keenergy_api.constants import ExternalHeatSource
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatPump
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import Photovoltaic
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import SolarCircuit
from keba_keenergy_api.constants import SwitchValve
from keba_keenergy_api.constants import System
from keba_keenergy_api.error import APIError

from .const import DOMAIN
from .const import MANUFACTURER
from .const import MANUFACTURER_INO
from .const import MANUFACTURER_MTEC
from .coordinator import KebaKeEnergyDataUpdateCoordinator

if TYPE_CHECKING:
    from keba_keenergy_api.endpoints import Value
_LOGGER = logging.getLogger(__name__)


class KebaKeEnergyEntity(
    CoordinatorEntity[KebaKeEnergyDataUpdateCoordinator],
):
    """KEBA KeEnergy base entity."""

    _attr_has_entity_name: bool = True

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
        key_index: int | None = None,
    ) -> None:
        """Initialize the KEBA KeEnergy entity."""
        super().__init__(coordinator)
        self.entry: ConfigEntry = entry
        self.section_id: str = section_id
        self.index: int | None = index
        self.key_index: int | None = key_index

        self._attr_unique_id: str | None = entry.unique_id

        if self.key_index is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.key_index + 1}"

        if self.position is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.position}"

    @property
    def position(self) -> int | None:
        """Return device position number."""
        _position: int | None = None if self.index is None else self.index + 1
        return _position

    @property
    def is_system_device(self) -> bool:
        """Return True if the entity is part of a KEBA KeEnergy control device else False."""
        return self.section_id in [SectionPrefix.SYSTEM]

    @property
    def is_heat_circuit(self) -> bool:
        """Return True if the entity is part of a heat circuit else False."""
        return self.section_id == SectionPrefix.HEAT_CIRCUIT

    @property
    def is_solar_circuit(self) -> bool:
        """Return True if the entity is part of a solar circuit else False."""
        return self.section_id == SectionPrefix.SOLAR_CIRCUIT

    @property
    def is_heat_pump(self) -> bool:
        """Return True if the entity is part of a heat pump else False."""
        return self.section_id == SectionPrefix.HEAT_PUMP

    @property
    def is_buffer_tank(self) -> bool:
        """Return True if the entity is part of a buffer tank else False."""
        return self.section_id == SectionPrefix.BUFFER_TANK

    @property
    def is_hot_water_tank(self) -> bool:
        """Return True if the entity is part of a hot water tank else False."""
        return self.section_id == SectionPrefix.HOT_WATER_TANK

    @property
    def is_external_heat_source(self) -> bool:
        """Return True if the entity is part of an external heat sources else False."""
        return self.section_id == SectionPrefix.EXTERNAL_HEAT_SOURCE

    @property
    def is_switch_valve(self) -> bool:
        """Return True if the entity is part of a switch valves else False."""
        return self.section_id == SectionPrefix.SWITCH_VALVE

    @property
    def is_photovoltaic(self) -> bool:
        """Return True if the entity is part of a photovoltaic else False."""
        return self.section_id == SectionPrefix.PHOTOVOLTAIC

    @property
    def device_name(self) -> str | None:
        """Return the device name and number."""
        return None

    @cached_property
    def device_identifier(self) -> str:
        """Return the device identifier."""
        _identifier: str = f"{self.entry.unique_id}_{DOMAIN if self.is_system_device else self.section_id}"

        # Add position number to identifier if there is more than one device
        # e.g. hot water tank, heat circuit, solar circuit or heat pump.

        if self.position is not None:
            _identifier = f"{_identifier}_{self.position}"

        return _identifier

    @cached_property
    def device_manufacturer(self) -> str | None:
        """Return the device manufacturer."""
        _manufacturer: str | None = None

        if self.is_system_device:
            _manufacturer = MANUFACTURER
        elif self.is_heat_pump:
            if self.coordinator.device_name.endswith("MTec"):
                _manufacturer = MANUFACTURER_MTEC
            elif self.coordinator.device_name.startswith("Bartl"):
                _manufacturer = MANUFACTURER_INO

        return _manufacturer

    @cached_property
    def device_model(self) -> str | None:
        """Return the device model."""
        _device_model: str | None = None

        # Add the model if we know it. We only know the model from the
        # KEBA KeEnergy control device and from the heat pump device.
        # We don't have model info from the hot water tank or the heat circuit.
        if self.is_system_device:
            _device_model = self.coordinator.device_model
        elif self.is_heat_pump:
            heat_pump_data: Value = self.coordinator.heat_pump_names[self.index or 0]
            _device_model = heat_pump_data["value"]

        return _device_model

    @cached_property
    def _translation_key(self) -> str | None:
        translation_key: str | None = None

        if self.is_system_device:
            translation_key = "control_unit"
        elif self.is_heat_circuit:
            translation_key = "heat_circuit"
        elif self.is_solar_circuit:
            translation_key = "solar_circuit"
        elif self.is_heat_pump:
            translation_key = "heat_pump"
        elif self.is_buffer_tank:
            translation_key = "buffer_tank"
        elif self.is_hot_water_tank:
            translation_key = "hot_water_tank"
        elif self.is_external_heat_source:
            translation_key = "external_heat_source"
        elif self.is_switch_valve:
            translation_key = "switch_valve"
        elif self.is_photovoltaic:
            translation_key = "photovoltaic"

        return translation_key

    @property
    def _translation_placeholders(self) -> Mapping[str, str] | None:
        return {
            "position": f" {self.position}" if self.position else "",
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return updated device specific attributes."""
        data: dict[str, Any] = {
            "name": self.device_name,
            "manufacturer": self.device_manufacturer,
            "model": self.device_model,
            "sw_version": (self.coordinator.device_hmi_sw_version if self.is_system_device else None),
            "translation_key": self._translation_key,
            "translation_placeholders": self._translation_placeholders,
            # Added via_device if the device is not the KEBA KeEnergy control device.
            "via_device": (None if self.is_system_device else (DOMAIN, f"{self.entry.unique_id}_{DOMAIN}")),
        }

        _device_info: DeviceInfo = DeviceInfo(
            configuration_url=self.coordinator.configuration_url,
            identifiers={(DOMAIN, self.device_identifier)},
            name=data["name"],
            model=data["model"],
            manufacturer=data["manufacturer"],
            sw_version=data["sw_version"],
            translation_key=data["translation_key"],
            translation_placeholders=data["translation_placeholders"],
            via_device=data["via_device"],
        )

        return _device_info

    async def _async_write_data(
        self,
        value: Any,
        /,
        *,
        section: Section | None = None,
        device_numbers: int | None = None,
    ) -> None:
        """Write data to the KEBA KeEnergy API."""
        if section:
            current_index: int = self.index or 0
            _range: int | None = device_numbers

            if _range and self.key_index is not None:
                quantity: int = section.value.quantity
                current_index = current_index * quantity + self.key_index
                _range = _range * quantity

            request: dict[Section, Any] = {
                section: (
                    [value if index == current_index else None for index in range(_range)]
                    if isinstance(_range, int)
                    else value
                ),
            }

            _LOGGER.debug("API write request %s", request)

            try:
                await self.coordinator.api.write_data(request=request)
            except (APIError, ClientError) as error:
                msg: str = f"Failed to update {self.entity_id} to {value}: {error}"
                raise HomeAssistantError(msg) from error

            self.coordinator.async_update_value(
                value,
                section_id=self.section_id,
                section=section,
                index=self.index or 0,
                key_index=self.key_index,
            )

            await self.coordinator.async_request_refresh()

    def get_attribute(self, key: str, /, *, attr: str) -> str:
        """Get extra attribute from the API by key."""
        data: list[list[Value]] | list[Value] | Value | None = self.coordinator.data[self.section_id].get(key, None)
        attributes: dict[str, Any] = {}

        if isinstance(data, list):
            data = data[self.index or 0]

        if isinstance(data, list) and self.key_index is not None:
            data = data[self.key_index]

        if isinstance(data, dict):
            attributes = data["attributes"]

        return str(attributes.get(attr, ""))

    def get_value(self, key: str, /) -> Any:
        """Get value from the API by key."""
        data: list[list[Value]] | list[Value] | Value | None = self.coordinator.data[self.section_id].get(key, None)
        value: Value | None = None

        if isinstance(data, list):
            data = data[self.index or 0]

        if isinstance(data, list) and self.key_index is not None:
            data = data[self.key_index]

        if isinstance(data, dict):
            value = data["value"]

        return value


class KebaKeEnergyExtendedEntity(KebaKeEnergyEntity):
    """KEBA KeEnergy base extended entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
        key_index: int | None = None,
    ) -> None:
        """Initialize the KEBA KeEnergy extended entity."""
        super().__init__(coordinator, entry=entry, section_id=section_id, index=index, key_index=key_index)
        self._attr_unique_id: str | None = f"{self.entry.unique_id}_{self.section_id}_{self.entity_description.key}"

        if self.is_system_device:
            self._attr_unique_id = f"{self.entry.unique_id}_{self.entity_description.key}"

        if self.key_index is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.key_index + 1}"

        if self.position is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.position}"

        self.device_numbers: int | None = None

    @property
    def section(self) -> Section | None:
        """Get the current section."""
        section: Section | None = None

        if self.is_system_device:
            section = System[self.entity_description.key.upper()]
        elif self.is_heat_circuit:
            section = HeatCircuit[self.entity_description.key.upper()]
            self.device_numbers = self.coordinator.heat_circuit_numbers
        elif self.is_solar_circuit:
            section = SolarCircuit[self.entity_description.key.upper()]
            self.device_numbers = self.coordinator.solar_circuit_numbers
        elif self.is_heat_pump:
            section = HeatPump[self.entity_description.key.upper()]
            self.device_numbers = self.coordinator.heat_pump_numbers
        elif self.is_buffer_tank:
            section = BufferTank[self.entity_description.key.upper()]
            self.device_numbers = self.coordinator.buffer_tank_numbers
        elif self.is_hot_water_tank:
            section = HotWaterTank[self.entity_description.key.upper()]
            self.device_numbers = self.coordinator.hot_water_tank_numbers
        elif self.is_external_heat_source:
            section = ExternalHeatSource[self.entity_description.key.upper()]
            self.device_numbers = self.coordinator.external_heat_source_numbers
        elif self.is_switch_valve:
            section = SwitchValve[self.entity_description.key.upper()]
            self.device_numbers = self.coordinator.switch_valve_numbers
        elif self.is_photovoltaic:
            section = Photovoltaic[self.entity_description.key.upper()]

        return section
