# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Entity classes for the KEBA KeEnergy integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any
from typing import Final
from typing import TypeVar
from typing import overload

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from keba_keenergy_api.constants import BufferTank
from keba_keenergy_api.constants import ExternalHeatSource
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HeatPump
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import SolarCircuit
from keba_keenergy_api.constants import System

from .const import DOMAIN
from .const import MANUFACTURER
from .const import MANUFACTURER_INO
from .const import MANUFACTURER_MTEC
from .coordinator import KebaKeEnergyConfigEntry
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .coordinator import get_value_by_index

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping
    from datetime import datetime

    from homeassistant.core import CALLBACK_TYPE
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType
    from keba_keenergy_api.endpoints import Value

_LOGGER = logging.getLogger(__name__)

DEVICE_TRANSLATION_KEYS: Final[dict[str, str]] = {
    SectionPrefix.SYSTEM: "control_unit",
    SectionPrefix.HEAT_CIRCUIT: "heat_circuit",
    SectionPrefix.SOLAR_CIRCUIT: "solar_circuit",
    SectionPrefix.HEAT_PUMP: "heat_pump",
    SectionPrefix.BUFFER_TANK: "buffer_tank",
    SectionPrefix.HOT_WATER_TANK: "hot_water_tank",
    SectionPrefix.EXTERNAL_HEAT_SOURCE: "external_heat_source",
    SectionPrefix.SWITCH_VALVE: "switch_valve",
    SectionPrefix.PASSIVE_COOLING: "passive_cooling",
    SectionPrefix.PHOTOVOLTAICS: "photovoltaics",
}

SECTIONS: Final[dict[str, type[Section]]] = {
    SectionPrefix.SYSTEM: System,
    SectionPrefix.HEAT_CIRCUIT: HeatCircuit,
    SectionPrefix.SOLAR_CIRCUIT: SolarCircuit,
    SectionPrefix.HEAT_PUMP: HeatPump,
    SectionPrefix.BUFFER_TANK: BufferTank,
    SectionPrefix.HOT_WATER_TANK: HotWaterTank,
    SectionPrefix.EXTERNAL_HEAT_SOURCE: ExternalHeatSource,
}

T = TypeVar("T", str, int, float)


@dataclass(frozen=True)
class KebaKeEnergyEntityDescriptionMixin:
    """Required values for KEBA KeEnergy descriptions."""

    key_index: int | None = None
    new_key: str | None = None  # new key name (required for future migration of the entity id)
    ref_key: str | None = None  # reference to another key (used for entity id)
    condition: Callable[[KebaKeEnergyDataUpdateCoordinator, int], bool] | None = None


class KebaKeEnergyBaseEntity(
    CoordinatorEntity[KebaKeEnergyDataUpdateCoordinator],
):
    """KEBA KeEnergy base entity."""

    _attr_has_entity_name: bool = True

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        entry: KebaKeEnergyConfigEntry,
        section_id: str,
        index: int | None,
        key_index: int | None = None,
    ) -> None:
        """Initialize the KEBA KeEnergy entity."""
        super().__init__(coordinator)
        self.entry: KebaKeEnergyConfigEntry = entry
        self.section_id: str = section_id
        self.index: int | None = index
        self.key_index: int | None = key_index

        self._attr_unique_id: str | None = entry.unique_id

        if self.key_index is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.key_index + 1}"

        if self.position is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.position}"

        self._async_call_later: CALLBACK_TYPE | None = None
        self._pending_value: float | None = None
        self._pending_key: str = ""
        self._pending_section: Section | None = None
        self._pending_device_numbers: int | None = None

    @property
    def position(self) -> int | None:
        """Return device position number."""
        _position: int | None = None if self.index is None else self.index + 1
        return _position

    @property
    def is_system_device(self) -> bool:
        """Return True if the entity is part of a KEBA KeEnergy control device else False."""
        return self.section_id == SectionPrefix.SYSTEM

    @property
    def is_heat_pump(self) -> bool:
        """Return True if the entity is part of a heat pump else False."""
        return self.section_id == SectionPrefix.HEAT_PUMP

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
        return DEVICE_TRANSLATION_KEYS.get(self.section_id)

    @property
    def _translation_placeholders(self) -> Mapping[str, str] | None:
        return {
            "position": f" {self.position}" if self.position else "",
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return updated device specific attributes."""
        data: dict[str, Any] = {
            "manufacturer": self.device_manufacturer,
            "model": self.device_model,
            "sw_version": (self.coordinator.device_hmi_sw_version if self.is_system_device else None),
            "translation_key": self._translation_key,
            "translation_placeholders": self._translation_placeholders,
        }

        _device_info: DeviceInfo = DeviceInfo(
            configuration_url=self.coordinator.configuration_url,
            identifiers={(DOMAIN, self.device_identifier)},
            model=data["model"],
            manufacturer=data["manufacturer"],
            sw_version=data["sw_version"],
            translation_key=data["translation_key"],
            translation_placeholders=data["translation_placeholders"],
        )

        if not self.is_system_device:
            _device_info["via_device_id"] = self.coordinator.control_unit_device_id

        return _device_info

    async def _async_write_data(
        self,
        value: object,
        /,
        *,
        section: Section,
        device_numbers: int | None = None,
        ignore_daily_write_count: bool = False,
    ) -> None:
        """Write data to the KEBA KeEnergy API."""
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

        self.coordinator.async_update_value(
            value,
            section_id=self.section_id,
            section=section,
            index=self.index or 0,
            key_index=self.key_index,
        )

        await self.coordinator.async_write_data(request=request, ignore_weekly_write_count=ignore_daily_write_count)

    async def _async_debounced_write_data(self, _: datetime) -> None:
        """Write data (debounced) to the KEBA KeEnergy API."""
        self._async_call_later = None

        current_value = self.get_value(self._pending_key, expected_type=float)

        if self._pending_section and self._pending_value is not None and self._pending_value != current_value:
            await self._async_write_data(
                self._pending_value,
                section=self._pending_section,
                device_numbers=self._pending_device_numbers,
            )

    def get_entity_data(self, key: str, /) -> Value | None:
        """Get the real entity data from the coordinator data."""
        values: list[list[Value]] | list[Value] | Value | None = self.coordinator.data[self.section_id].get(key)
        return None if values is None else get_value_by_index(values, index=self.index, key_index=self.key_index)

    def get_attribute(self, key: str, /, *, attr: str) -> str:
        """Get extra attribute from the API by key."""
        entity_data: Value | None = self.get_entity_data(key)
        attributes: dict[str, Any] = entity_data.get("attributes", {}) if entity_data else {}
        return str(attributes.get(attr, ""))

    @overload
    def get_value(self, key: str, /, *, expected_type: type[T]) -> T | None: ...

    @overload
    def get_value(self, key: str, /) -> StateType: ...

    def get_value(self, key: str, /, *, expected_type: type[T] | None = None) -> StateType:
        """Get value from the API by key."""
        entity_data: Value | None = self.get_entity_data(key)
        value: StateType = None

        if isinstance(entity_data, dict):
            value = entity_data["value"]

        if expected_type and value is not None:
            return expected_type(value)

        return value


class KebaKeEnergyEntity(KebaKeEnergyBaseEntity):
    """KEBA KeEnergy base extended entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        entry: KebaKeEnergyConfigEntry,
        section_id: str,
        index: int | None,
        key_index: int | None = None,
    ) -> None:
        """Initialize the KEBA KeEnergy extended entity."""
        super().__init__(coordinator, entry=entry, section_id=section_id, index=index, key_index=key_index)

        self._attr_unique_id: str | None = self.get_unique_id(self.entity_description.key)

    def get_unique_id(self, key: str, /) -> str | None:
        """Generate unique id."""
        unique_id: str | None = f"{self.entry.unique_id}_{self.section_id}_{key}"

        if self.is_system_device:
            unique_id = f"{self.entry.unique_id}_{key}"

        if self.key_index is not None:
            unique_id = f"{unique_id}_{self.key_index + 1}"

        if self.position is not None:
            unique_id = f"{unique_id}_{self.position}"

        return unique_id

    @property
    def section(self) -> Section:
        """Get the section of the entity description key."""
        return SECTIONS[self.section_id][self.entity_description.key.upper()]

    @property
    def device_numbers(self) -> int | None:
        """Return the number of devices of the section, or None for the control unit."""
        return None if self.is_system_device else getattr(self.coordinator.position, self.section_id, 0)


async def _async_setup_entities(
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
    entity_types: dict[str, tuple[Any, ...]],
    entity_cls: type[Any],
    entity_name: str,
) -> None:
    """Set up KEBA KeEnergy entities."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data
    entities: list[Any] = []

    for section_id, section_data in coordinator.data.items():
        for description in entity_types.get(section_id, ()):
            for key, values in section_data.items():
                if key not in (description.key, description.new_key):
                    continue

                device_numbers = len(values) if isinstance(values, list) else 1

                for index in range(device_numbers):
                    if description.condition is not None and not description.condition(coordinator, index):
                        _LOGGER.debug(
                            'Skip %s with key "%s" (index: %s)',
                            entity_name,
                            description.ref_key or description.key,
                            index,
                        )
                        continue

                    _LOGGER.debug(
                        'Add %s with key "%s" (index: %s)',
                        entity_name,
                        description.ref_key or description.key,
                        index,
                    )

                    cls: type[Any] = getattr(description, "entity_class", entity_cls)

                    entities.append(
                        cls(
                            coordinator=coordinator,
                            description=description,
                            entry=entry,
                            section_id=section_id,
                            index=index if device_numbers > 1 else None,
                        ),
                    )

    async_add_entities(entities)
