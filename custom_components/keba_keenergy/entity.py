# Copyright 2025-2026 Michael Hacker
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

from homeassistant.core import HassJob
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_call_later
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

from .const import ATTR_MESSAGE_ID
from .const import DOMAIN
from .const import FLASH_WRITE_DELAY
from .const import MANUFACTURER
from .const import MANUFACTURER_INO
from .const import MANUFACTURER_MTEC
from .coordinator import KebaKeEnergyConfigEntry
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .coordinator import Values
from .coordinator import get_device_identifier
from .coordinator import get_value_by_index

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping
    from datetime import datetime

    from homeassistant.core import CALLBACK_TYPE
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType
    from keba_keenergy_api.endpoints import Value

_LOGGER: Final = logging.getLogger(__name__)

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
    new_key: str | None = None  # New key name, required for a future migration of the entity ID.
    ref_key: str | None = None  # Reference to another key, used for the entity ID.
    condition: Callable[[KebaKeEnergyDataUpdateCoordinator, int], bool] | None = None
    entity_class: type[Any] | None = None  # Entity class instead of the default class of the platform.


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

        self._attr_unique_id: str | None = self._build_unique_id()

        self._async_call_later: CALLBACK_TYPE | None = None
        self._pending_value: float | None = None
        self._pending_key: str = ""
        self._pending_section: Section | None = None

    def _build_unique_id(self, *parts: str) -> str:
        """Return `<entry unique_id>[_<part>...][_<key_index + 1>][_<index + 1>]`."""
        unique_id: str = "_".join((str(self.entry.unique_id), *parts))

        if self.key_index is not None:
            unique_id = f"{unique_id}_{self.key_index + 1}"

        if self.position is not None:
            unique_id = f"{unique_id}_{self.position}"

        return unique_id

    async def async_will_remove_from_hass(self) -> None:
        """Cancel a pending debounced write when the entity is removed."""
        if self._async_call_later:
            self._async_call_later()
            self._async_call_later = None

        await super().async_will_remove_from_hass()

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

    @property
    def device_numbers(self) -> int | None:
        """Return the number of devices of the section, or None for the control unit."""
        return None if self.is_system_device else self.coordinator.device_count(self.section_id)

    @cached_property
    def device_identifier(self) -> str:
        """Return the device identifier."""
        return get_device_identifier(self.entry.unique_id, self.section_id, self.position)

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
        _device_info: DeviceInfo = DeviceInfo(
            configuration_url=self.coordinator.configuration_url,
            identifiers={(DOMAIN, self.device_identifier)},
            model=self.device_model,
            manufacturer=self.device_manufacturer,
            sw_version=self.coordinator.device_hmi_sw_version if self.is_system_device else None,
            translation_key=self._translation_key,
            translation_placeholders=self._translation_placeholders,
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
        ignore_weekly_write_count: bool = False,
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

        previous_value: object = self.coordinator.async_update_value(
            value,
            section_id=self.section_id,
            section=section,
            index=self.index or 0,
            key_index=self.key_index,
        )

        try:
            await self.coordinator.async_write_data(
                request=request, ignore_weekly_write_count=ignore_weekly_write_count
            )
        except HomeAssistantError:
            # The control unit still has the previous value, so the entity shows it again. Only this value is reset,
            # other values may have changed while the write waited for the lock.
            self.coordinator.async_set_value(
                previous_value,
                section_id=self.section_id,
                key=section.name.lower(),
                index=self.index or 0,
                key_index=self.key_index,
            )
            raise

    def _schedule_debounced_write(self, value: float | None, /) -> None:
        """Write the value after `FLASH_WRITE_DELAY`, a new value restarts the delay.

        Without a value (None) a pending write is kept.
        """
        if value is None:
            return

        self._pending_value = value

        if self._async_call_later:
            self._async_call_later()

        self._async_call_later = async_call_later(
            hass=self.hass,
            delay=FLASH_WRITE_DELAY,
            action=HassJob(
                self._async_debounced_write_data,
                cancel_on_shutdown=True,
            ),
        )

    async def _async_debounced_write_data(self, _: datetime) -> None:
        """Write data (debounced) to the KEBA KeEnergy API."""
        self._async_call_later = None

        current_value: float | None = self.get_value(self._pending_key, expected_type=float)

        if self._pending_section and self._pending_value is not None and self._pending_value != current_value:
            try:
                await self._async_write_data(
                    self._pending_value,
                    section=self._pending_section,
                    device_numbers=self.device_numbers,
                )
            except HomeAssistantError as error:
                # No caller gets the error of a debounced write, the entity already shows the previous value again.
                _LOGGER.warning("Failed to write the value of %s: %s", self.entity_id, error)

    def _get_debounced_value(self) -> float | None:
        """Return the value that waits for the debounced write, otherwise the current value."""
        if self._pending_value is not None and self._async_call_later:
            return self._pending_value

        return self.get_value(self._pending_key, expected_type=float)

    def get_entity_data(self, key: str, /) -> Value | None:
        """Get the real entity data from the coordinator data, or None if the sensor is not in use."""
        if not self.coordinator.is_sensor_in_use(self.section_id, key, index=self.index, key_index=self.key_index):
            return None

        values: Values | None = self.coordinator.data[self.section_id].get(key)
        return None if values is None else get_value_by_index(values, index=self.index, key_index=self.key_index)

    def get_attribute(self, key: str, /, *, attr: str) -> str:
        """Get extra attribute from the API by key."""
        entity_data: Value | None = self.get_entity_data(key)
        attributes: dict[str, Any] = entity_data.get("attributes", {}) if entity_data else {}
        return str(attributes.get(attr, ""))

    def get_limit(self, key: str, /, *, attr: str) -> float | None:
        """Get a limit (e.g. `lower_limit`) from the API by key, or None if the value has no valid limit."""
        try:
            return float(self.get_attribute(key, attr=attr))
        except ValueError:
            return None

    @overload
    def get_value(self, key: str, /, *, expected_type: type[T]) -> T | None: ...

    @overload
    def get_value(self, key: str, /) -> StateType: ...

    def get_value(self, key: str, /, *, expected_type: type[T] | None = None) -> StateType:
        """Get value from the API by key."""
        entity_data: Value | None = self.get_entity_data(key)
        value: StateType = entity_data.get("value") if entity_data else None

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
        return self._build_unique_id(key) if self.is_system_device else self._build_unique_id(self.section_id, key)

    @property
    def section(self) -> Section:
        """Get the section of the entity description key."""
        return SECTIONS[self.section_id][self.entity_description.key.upper()]

    def _message_id_attributes(self, key: str, /) -> dict[str, int]:
        """Return the message id of the sensor as attribute (0 means the sensor is in use), if the sensor has one."""
        message_id: int | None = self.coordinator.get_message_id(
            self.section_id,
            key,
            index=self.index,
            key_index=self.key_index,
        )
        return {} if message_id is None else {ATTR_MESSAGE_ID: message_id}


@callback
def _async_setup_entities(
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
            for key in (description.key, description.new_key):
                values: Values | None = section_data.get(key) if key else None

                if values is None:
                    continue

                device_numbers: int = len(values) if isinstance(values, list) else 1

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

                    cls: type[Any] = description.entity_class or entity_cls

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
