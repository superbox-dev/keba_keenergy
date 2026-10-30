# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Entity classes for the KEBA KeEnergy integration."""

from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Final
from typing import Literal

from homeassistant.core import HassJob
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_TRANSLATION_KEYS
from .const import DOMAIN
from .const import FLASH_WRITE_DELAY
from .const import FLOAT32_SIGNIFICANT_DIGITS
from .const import MANUFACTURER
from .const import MANUFACTURER_INO
from .const import MANUFACTURER_MTEC
from .const import SectionPrefix
from .coordinator import KebaKeEnergyConfigEntry
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .legacy import get_data_key
from .legacy import get_data_keys

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping
    from datetime import datetime

    from homeassistant.core import CALLBACK_TYPE
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from keba_keenergy_api.endpoints import EndpointType
    from keba_keenergy_api.models import Reading
    from keba_keenergy_api.models import Value
    from keba_keenergy_api.models import WriteValue

_LOGGER: Final = logging.getLogger(__name__)

# Condition of an entity description, called with the coordinator and the index of the device.
type EntityCondition = Callable[[KebaKeEnergyDataUpdateCoordinator, int], bool]


@dataclass(frozen=True, kw_only=True)
class KebaKeEnergyEntityDescription(EntityDescription):
    """Shared values of the KEBA KeEnergy entity descriptions."""

    value_index: int | None = None
    new_key: str | None = None  # New key name, required for a future migration of the entity ID.
    ref_key: str | None = None  # Name in the unique ID instead of the key, for a second entity on the same value.
    condition: EntityCondition | None = None
    entity_class: type[KebaKeEnergyEntity] | None = None  # Entity class instead of the default class of the platform.


class KebaKeEnergyBaseEntity(
    CoordinatorEntity[KebaKeEnergyDataUpdateCoordinator],
):
    """KEBA KeEnergy base entity."""

    _attr_has_entity_name: bool = True
    # Domain of the platform, the entity ID is `<platform domain>.<domain>_<unique ID>`.
    _platform_domain: str

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        /,
        *,
        device_type: SectionPrefix,
        index: int | None,
        value_index: int | None = None,
    ) -> None:
        """Initialize the KEBA KeEnergy entity of the device with the index (None if it is the only one)."""
        super().__init__(coordinator)
        self.device_type: SectionPrefix = device_type
        self.index: int | None = index
        self.value_index: int | None = value_index

        self._attr_unique_id: str | None = self._build_unique_id(*self._unique_id_parts)
        self.entity_id: str = f"{self._platform_domain}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def _unique_id_parts(self) -> tuple[str, ...]:
        """Return the parts of the unique ID between the entry unique ID and the indexes."""
        # TODO: Remove this default when the unique IDs of the climate and DHW tank entities are migrated to
        #  `<serial>_<device type>[_<n>]`, every entity then returns its parts itself.
        return ()

    def _build_unique_id(self, *parts: str) -> str:
        """Return `<entry unique_id>[_<part>...][_<value_index + 1>][_<index + 1>]`."""
        unique_id: str = "_".join((str(self.coordinator.config_entry.unique_id), *parts))

        if self.value_index is not None:
            unique_id = f"{unique_id}_{self.value_index + 1}"

        if self.device_number is not None:
            unique_id = f"{unique_id}_{self.device_number}"

        return unique_id

    @property
    def device_number(self) -> int | None:
        """Return the number of the device (from 1), None if the device type has only one device."""
        return None if self.index is None else self.index + 1

    @property
    def is_system_device(self) -> bool:
        """Return True if the entity is part of the control unit else False."""
        return self.device_type == SectionPrefix.SYSTEM

    @property
    def is_heat_pump(self) -> bool:
        """Return True if the entity is part of a heat pump else False."""
        return self.device_type == SectionPrefix.HEAT_PUMP

    @cached_property
    def device_identifier(self) -> str:
        """Return the device identifier."""
        return self.coordinator.device_identifier(self.device_type, self.device_number)

    @cached_property
    def device_manufacturer(self) -> str | None:
        """Return the device manufacturer."""
        if self.is_system_device:
            return MANUFACTURER

        if self.is_heat_pump:
            if self.coordinator.device_name.endswith("MTec"):
                return MANUFACTURER_MTEC

            if self.coordinator.device_name.startswith("Bartl"):
                return MANUFACTURER_INO

        return None

    @cached_property
    def device_model(self) -> str | None:
        """Return the device model."""
        # Only the control unit and the heat pumps report a model, the other devices have none.
        if self.is_system_device:
            return self.coordinator.device_model

        if self.is_heat_pump:
            return self.coordinator.heat_pump_names[self.index or 0]

        return None

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device of the entity, the control unit is the parent of all other devices."""
        device_info: DeviceInfo = DeviceInfo(
            configuration_url=self.coordinator.configuration_url,
            identifiers={(DOMAIN, self.device_identifier)},
            model=self.device_model,
            manufacturer=self.device_manufacturer,
            sw_version=self.coordinator.device_hmi_sw_version if self.is_system_device else None,
            translation_key=self._translation_key,
            translation_placeholders=self._translation_placeholders,
        )

        if not self.is_system_device:
            device_info["via_device_id"] = self.coordinator.control_unit_device_id

        return device_info

    @cached_property
    def _translation_key(self) -> str | None:
        return DEVICE_TRANSLATION_KEYS.get(self.device_type)

    @property
    def _translation_placeholders(self) -> Mapping[str, str]:
        return {
            "device_number": f" {self.device_number}" if self.device_number else "",
        }

    def get_reading(self, key: str, /) -> Reading | None:
        """Get the reading of the entity from the coordinator data, or None if the sensor is not in use."""
        if not self.coordinator.is_sensor_in_use(self.device_type, key, index=self.index, value_index=self.value_index):
            return None

        return self.coordinator.get_reading(self.device_type, key, index=self.index, value_index=self.value_index)

    def get_limit(self, key: str, /, *, attr: Literal["lower_limit", "upper_limit"]) -> float | None:
        """Return a limit of the value of the key, None if the value has no limit or the sensor is not in use."""
        reading: Reading | None = self.get_reading(key)
        return None if reading is None else getattr(reading, attr)

    def get_value(self, key: str, /) -> Value | None:
        """Return the value of the key, None if it is missing or the sensor is not in use."""
        reading: Reading | None = self.get_reading(key)
        return None if reading is None else reading.value

    def get_typed_value[T](self, key: str, value_type: type[T], /) -> T | None:
        """Return the value of the key, None if it is not of the type, missing or the sensor is not in use."""
        value: Value | None = self.get_value(key)
        return value if isinstance(value, value_type) else None

    def get_float(self, key: str, /) -> float | None:
        """Return the numeric value of the key as float, None if it is not a number (also a bool) or missing."""
        value: Value | None = self.get_value(key)
        return float(value) if isinstance(value, float | int) and not isinstance(value, bool) else None

    async def _async_write_value(
        self,
        value: WriteValue,
        /,
        *,
        key: str,
        ignore_weekly_write_count: bool = False,
    ) -> None:
        """Write the value of the key of this entity to the control unit.

        The entity shows the value at once, if the write fails it shows the previous value again.
        """
        reading_index: int = self.coordinator.reading_index(
            self.device_type,
            key,
            index=self.index,
            value_index=self.value_index,
        )
        quantity: int = self.coordinator.get_endpoint(self.device_type, key).value.quantity
        # The values of all devices, the control unit has no device count and has the values of one device.
        reading_count: int = (self.coordinator.device_count(self.device_type) or 1) * quantity
        values: list[WriteValue | None] = [value if index == reading_index else None for index in range(reading_count)]

        previous_value: Value = self.coordinator.async_set_local_value(
            value,
            device_type=self.device_type,
            key=key,
            index=self.index,
            value_index=self.value_index,
        )

        try:
            await self.coordinator.async_write_data(
                self.device_type,
                {key: values},
                ignore_weekly_write_count=ignore_weekly_write_count,
            )
        except HomeAssistantError:
            # The control unit still has the previous value, so the entity shows it again. Only this value is reset,
            # other values may have changed while the write waited for the lock.
            self.coordinator.async_set_local_value(
                previous_value,
                device_type=self.device_type,
                key=key,
                index=self.index,
                value_index=self.value_index,
            )
            raise

    @staticmethod
    def _round_float32(value: float, /) -> float:
        """Round a value to the significant digits of a Float32, the Web HMI returns `0.8` as `0.80000001`."""
        return float(f"{value:.{FLOAT32_SIGNIFICANT_DIGITS}g}")


class KebaKeEnergyDebouncedEntity(KebaKeEnergyBaseEntity):
    """KEBA KeEnergy entity that writes a fast-changing value debounced, to limit the writes to the flash."""

    _cancel_debounced_write: CALLBACK_TYPE | None = None
    _pending_value: float | None = None

    @property
    @abstractmethod
    def _debounced_key(self) -> str:
        """Return the key of the value that is written debounced."""

    async def async_will_remove_from_hass(self) -> None:
        """Cancel a pending debounced write when the entity is removed."""
        if self._cancel_debounced_write:
            self._cancel_debounced_write()
            self._cancel_debounced_write = None

        await super().async_will_remove_from_hass()

    def _schedule_debounced_write(self, value: float | None, /) -> None:
        """Write the value after `FLASH_WRITE_DELAY`, a new value restarts the delay.

        Without a value (None) a pending write is kept.
        """
        if value is None:
            return

        # The API only writes integers to integer values, e.g. a runtime in seconds.
        value_type: EndpointType = self.coordinator.get_endpoint(self.device_type, self._debounced_key).value.value_type
        self._pending_value = round(value) if value_type is int else self._round_float32(value)

        if self._cancel_debounced_write:
            self._cancel_debounced_write()

        self._cancel_debounced_write = async_call_later(
            hass=self.hass,
            delay=FLASH_WRITE_DELAY,
            action=HassJob(
                self._async_debounced_write_data,
                cancel_on_shutdown=True,
            ),
        )

    async def _async_debounced_write_data(self, _now: datetime, /) -> None:
        """Write the pending value if it differs from the current value, `_now` is the time of the timer."""
        self._cancel_debounced_write = None

        if self._pending_value is not None and self._pending_value != self._get_current_value():
            try:
                await self._async_write_value(self._pending_value, key=self._debounced_key)
            except HomeAssistantError as error:
                # No caller gets the error of a debounced write, the entity already shows the previous value again.
                _LOGGER.warning("Failed to write the value of %s: %s", self.entity_id, error)

    def _get_current_value(self) -> float | None:
        """Return the current value of the debounced key, a float rounded to the significant digits of a Float32."""
        value: float | None = self.get_typed_value(self._debounced_key, float)
        return self.get_float(self._debounced_key) if value is None else self._round_float32(value)

    def _get_debounced_value(self) -> float | None:
        """Return the value that waits for the debounced write, otherwise the current value."""
        if self._pending_value is not None and self._cancel_debounced_write:
            return self._pending_value

        return self._get_current_value()


class KebaKeEnergyEntity(KebaKeEnergyBaseEntity):
    """KEBA KeEnergy entity with an entity description."""

    entity_description: KebaKeEnergyEntityDescription

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: KebaKeEnergyEntityDescription,
        /,
        *,
        device_type: SectionPrefix,
        index: int | None,
    ) -> None:
        """Initialize the KEBA KeEnergy entity of the device with the index (None if it is the only one)."""
        self.entity_description = description

        super().__init__(coordinator, device_type=device_type, index=index, value_index=description.value_index)

    @property
    def _unique_id_parts(self) -> tuple[str, ...]:
        """Return the key (or `ref_key`), with the device type except for the control unit."""
        key: str = self.entity_description.ref_key or self.entity_description.key
        return (key,) if self.is_system_device else (self.device_type, key)

    @property
    def _data_key(self) -> str:
        """Return the key of the value in the coordinator data, the new key if the API renamed it."""
        return get_data_key(self.entity_description)


@callback
def async_setup_entities(
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
    entity_types: Mapping[SectionPrefix, tuple[KebaKeEnergyEntityDescription, ...]],
    default_entity_class: type[KebaKeEnergyEntity],
    platform_name: str,
) -> None:
    """Set up the entities of a platform, `platform_name` is only used in the logs."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = entry.runtime_data
    entities: list[KebaKeEnergyEntity] = []
    deactivated_unique_ids: set[str | None] = set()

    for device_type, readings_by_key in coordinator.data.items():
        for description in entity_types.get(device_type, ()):
            for key in get_data_keys(description):
                readings: list[Reading] | None = readings_by_key.get(key)

                if not readings:
                    continue

                quantity: int = coordinator.get_endpoint(device_type, key).value.quantity
                device_count: int = len(readings) // quantity

                for index in range(device_count):
                    if description.condition is not None and not description.condition(coordinator, index):
                        _LOGGER.debug(
                            'Skip %s with key "%s" (index: %s)',
                            platform_name,
                            description.ref_key or description.key,
                            index,
                        )
                        continue

                    entity_class: type[KebaKeEnergyEntity] = description.entity_class or default_entity_class
                    entity: KebaKeEnergyEntity = entity_class(
                        coordinator,
                        description,
                        device_type=device_type,
                        index=index if device_count > 1 else None,
                    )

                    # A deactivated sensor is not configured on the control unit, the Web HMI hides it as well.
                    if coordinator.is_sensor_deactivated(
                        device_type,
                        key,
                        index=entity.index,
                        value_index=entity.value_index,
                    ):
                        _LOGGER.debug(
                            'Skip deactivated %s with key "%s" (index: %s)',
                            platform_name,
                            description.ref_key or description.key,
                            index,
                        )
                        deactivated_unique_ids.add(entity.unique_id)
                        continue

                    entities.append(entity)

    _async_remove_deactivated_entities(entry, deactivated_unique_ids)
    async_add_entities(entities)


@callback
def _async_remove_deactivated_entities(entry: KebaKeEnergyConfigEntry, unique_ids: set[str | None], /) -> None:
    """Remove the entities of deactivated sensors that were created before from the entity registry."""
    entity_registry: er.EntityRegistry = er.async_get(entry.runtime_data.hass)

    for registry_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
        if registry_entry.unique_id in unique_ids:
            _LOGGER.debug("Remove entity %s of a deactivated sensor", registry_entry.entity_id)
            entity_registry.async_remove(registry_entry.entity_id)


def has_photovoltaics(coordinator: KebaKeEnergyDataUpdateCoordinator, _: int) -> bool:
    """Return True if the control unit has photovoltaics, condition of an entity description."""
    return coordinator.has_photovoltaics()


def has_electrical_energy_meter(coordinator: KebaKeEnergyDataUpdateCoordinator, index: int) -> bool:
    """Return True if the heat pump has an electrical energy meter, condition of an entity description."""
    return coordinator.has_electrical_energy_meter(index=index)


def has_heat_meter(coordinator: KebaKeEnergyDataUpdateCoordinator, index: int) -> bool:
    """Return True if the heat pump has a heat meter, condition of an entity description."""
    return coordinator.has_heat_meter(index=index)


def has_both_meters(coordinator: KebaKeEnergyDataUpdateCoordinator, index: int) -> bool:
    """Return True if the heat pump has an electrical energy and a heat meter, condition of an entity description."""
    return coordinator.has_electrical_energy_meter(index=index) and coordinator.has_heat_meter(index=index)


def has_electrical_energy_meter_and_cooling(coordinator: KebaKeEnergyDataUpdateCoordinator, index: int) -> bool:
    """Return True if the heat pump has an electrical energy meter and cools, condition of an entity description."""
    return coordinator.has_electrical_energy_meter(index=index) and coordinator.has_cooling(index=index)


def is_heating_circuit(coordinator: KebaKeEnergyDataUpdateCoordinator, index: int) -> bool:
    """Return True if the heating circuit heats, condition of an entity description."""
    return coordinator.is_heating_circuit(index=index)


def is_cooling_circuit(coordinator: KebaKeEnergyDataUpdateCoordinator, index: int) -> bool:
    """Return True if the heating circuit cools, condition of an entity description."""
    return coordinator.is_cooling_circuit(index=index)


def is_cooling_only_circuit(coordinator: KebaKeEnergyDataUpdateCoordinator, index: int) -> bool:
    """Return True if the heating circuit only cools, condition of an entity description."""
    return coordinator.is_cooling_circuit(index=index) and not coordinator.is_heating_circuit(index=index)


def is_heating_circuit_with_photovoltaics(coordinator: KebaKeEnergyDataUpdateCoordinator, index: int) -> bool:
    """Return True if the heating circuit heats with photovoltaics, condition of an entity description."""
    return coordinator.is_heating_circuit(index=index) and coordinator.has_photovoltaics()


def is_cooling_circuit_with_photovoltaics(coordinator: KebaKeEnergyDataUpdateCoordinator, index: int) -> bool:
    """Return True if the heating circuit cools with photovoltaics, condition of an entity description."""
    return coordinator.is_cooling_circuit(index=index) and coordinator.has_photovoltaics()
