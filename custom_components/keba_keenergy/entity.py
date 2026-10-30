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
from typing import Literal

from homeassistant.core import HassJob
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
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
from .legacy import get_data_keys

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping
    from datetime import datetime

    from homeassistant.core import CALLBACK_TYPE
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from keba_keenergy_api.models import Reading
    from keba_keenergy_api.models import Value
    from keba_keenergy_api.models import WriteValue

_LOGGER: Final = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class KebaKeEnergyEntityDescription:
    """Shared values of the KEBA KeEnergy entity descriptions."""

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
        device_type: str,
        index: int | None,
        key_index: int | None = None,
    ) -> None:
        """Initialize the KEBA KeEnergy entity."""
        super().__init__(coordinator)
        self.entry: KebaKeEnergyConfigEntry = entry
        self.device_type: str = device_type
        self.index: int | None = index
        self.key_index: int | None = key_index

        self._attr_unique_id: str | None = self._build_unique_id()

        self._async_call_later: CALLBACK_TYPE | None = None
        self._pending_value: float | None = None
        self._pending_key: str = ""

    def _build_unique_id(self, *parts: str) -> str:
        """Return `<entry unique_id>[_<part>...][_<key_index + 1>][_<index + 1>]`."""
        unique_id: str = "_".join((str(self.entry.unique_id), *parts))

        if self.key_index is not None:
            unique_id = f"{unique_id}_{self.key_index + 1}"

        if self.device_number is not None:
            unique_id = f"{unique_id}_{self.device_number}"

        return unique_id

    @property
    def device_number(self) -> int | None:
        """Return the number of the device (from 1), None if the device type has only one device."""
        return None if self.index is None else self.index + 1

    @property
    def is_system_device(self) -> bool:
        """Return True if the entity is part of a KEBA KeEnergy control device else False."""
        return self.device_type == SectionPrefix.SYSTEM

    @property
    def is_heat_pump(self) -> bool:
        """Return True if the entity is part of a heat pump else False."""
        return self.device_type == SectionPrefix.HEAT_PUMP

    @property
    def device_numbers(self) -> int | None:
        """Return the number of devices of the device type, or None for the control unit."""
        return None if self.is_system_device else self.coordinator.device_count(self.device_type)

    @cached_property
    def device_identifier(self) -> str:
        """Return the device identifier."""
        return self.coordinator.device_identifier(self.device_type, self.device_number)

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
            _device_model = self.coordinator.heat_pump_names[self.index or 0]

        return _device_model

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

    @cached_property
    def _translation_key(self) -> str | None:
        return DEVICE_TRANSLATION_KEYS.get(self.device_type)

    @property
    def _translation_placeholders(self) -> Mapping[str, str] | None:
        return {
            "device_number": f" {self.device_number}" if self.device_number else "",
        }

    async def async_will_remove_from_hass(self) -> None:
        """Cancel a pending debounced write when the entity is removed."""
        if self._async_call_later:
            self._async_call_later()
            self._async_call_later = None

        await super().async_will_remove_from_hass()

    def get_reading(self, key: str, /) -> Reading | None:
        """Get the reading of the entity from the coordinator data, or None if the sensor is not in use."""
        if not self.coordinator.is_sensor_in_use(self.device_type, key, index=self.index, key_index=self.key_index):
            return None

        return self.coordinator.get_reading(self.device_type, key, index=self.index, key_index=self.key_index)

    def get_limit(self, key: str, /, *, attr: Literal["lower_limit", "upper_limit"]) -> float | None:
        """Get a limit of the value from the API by key, or None if the value has no limit."""
        reading: Reading | None = self.get_reading(key)
        return None if reading is None else getattr(reading, attr)

    def get_value(self, key: str, /) -> Value | None:
        """Get value from the API by key."""
        reading: Reading | None = self.get_reading(key)
        return None if reading is None else reading.value

    def get_typed_value[T](self, key: str, value_type: type[T], /) -> T | None:
        """Get value from the API by key, or None if it is not of the type."""
        value: Value | None = self.get_value(key)
        return value if isinstance(value, value_type) else None

    def get_float(self, key: str, /) -> float | None:
        """Get a numeric value from the API by key as float."""
        value: Value | None = self.get_value(key)
        return float(value) if isinstance(value, float | int) and not isinstance(value, bool) else None

    async def _async_write_data(
        self,
        value: WriteValue,
        /,
        *,
        key: str,
        device_numbers: int | None = None,
        ignore_weekly_write_count: bool = False,
    ) -> None:
        """Write data to the KEBA KeEnergy API."""
        current_index: int = self.index or 0
        _range: int = device_numbers or 1

        if self.key_index is not None:
            quantity: int = self.coordinator.get_endpoint(self.device_type, key).value.quantity
            current_index = current_index * quantity + self.key_index
            _range = _range * quantity

        values: list[WriteValue | None] = [value if index == current_index else None for index in range(_range)]

        previous_value: Value = self.coordinator.async_set_local_value(
            value,
            device_type=self.device_type,
            key=key,
            index=self.index,
            key_index=self.key_index,
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
                key_index=self.key_index,
            )
            raise

    def _schedule_debounced_write(self, value: float | None, /) -> None:
        """Write the value after `FLASH_WRITE_DELAY`, a new value restarts the delay.

        Without a value (None) a pending write is kept.
        """
        if value is None:
            return

        # The API only writes integers to integer values, e.g. a runtime in seconds.
        value_type: type = self.coordinator.get_endpoint(self.device_type, self._pending_key).value.value_type
        self._pending_value = round(value) if value_type is int else self._round_float32(value)

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

    @staticmethod
    def _round_float32(value: float, /) -> float:
        """Round a value to the significant digits of a Float32, the Web HMI returns `0.8` as `0.80000001`."""
        return float(f"{value:.{FLOAT32_SIGNIFICANT_DIGITS}g}")

    async def _async_debounced_write_data(self, _: datetime) -> None:
        """Write data (debounced) to the KEBA KeEnergy API."""
        self._async_call_later = None

        if self._pending_key and self._pending_value is not None and self._pending_value != self._get_current_value():
            try:
                await self._async_write_data(
                    self._pending_value,
                    key=self._pending_key,
                    device_numbers=self.device_numbers,
                )
            except HomeAssistantError as error:
                # No caller gets the error of a debounced write, the entity already shows the previous value again.
                _LOGGER.warning("Failed to write the value of %s: %s", self.entity_id, error)

    def _get_current_value(self) -> float | None:
        """Return the current value of the pending key, a float rounded to the significant digits of a Float32."""
        value: float | None = self.get_typed_value(self._pending_key, float)
        return self.get_float(self._pending_key) if value is None else self._round_float32(value)

    def _get_debounced_value(self) -> float | None:
        """Return the value that waits for the debounced write, otherwise the current value."""
        if self._pending_value is not None and self._async_call_later:
            return self._pending_value

        return self._get_current_value()


class KebaKeEnergyEntity(KebaKeEnergyBaseEntity):
    """KEBA KeEnergy base extended entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        entry: KebaKeEnergyConfigEntry,
        device_type: str,
        index: int | None,
        key_index: int | None = None,
    ) -> None:
        """Initialize the KEBA KeEnergy extended entity."""
        super().__init__(coordinator, entry=entry, device_type=device_type, index=index, key_index=key_index)

        self._attr_unique_id: str | None = self.get_unique_id(self.entity_description.key)

    def get_unique_id(self, key: str, /) -> str | None:
        """Generate unique id."""
        return self._build_unique_id(key) if self.is_system_device else self._build_unique_id(self.device_type, key)


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
    deactivated_unique_ids: set[str] = set()

    for device_type, readings_by_key in coordinator.data.items():
        for description in entity_types.get(device_type, ()):
            for key in get_data_keys(description):
                readings: list[Reading] | None = readings_by_key.get(key)

                if not readings:
                    continue

                quantity: int = coordinator.get_endpoint(device_type, key).value.quantity
                device_numbers: int = len(readings) // quantity

                for index in range(device_numbers):
                    if description.condition is not None and not description.condition(coordinator, index):
                        _LOGGER.debug(
                            'Skip %s with key "%s" (index: %s)',
                            entity_name,
                            description.ref_key or description.key,
                            index,
                        )
                        continue

                    cls: type[Any] = description.entity_class or entity_cls
                    entity: Any = cls(
                        coordinator=coordinator,
                        description=description,
                        entry=entry,
                        device_type=device_type,
                        index=index if device_numbers > 1 else None,
                    )

                    # A deactivated sensor is not configured on the control unit, the Web HMI hides it as well.
                    if coordinator.is_sensor_deactivated(
                        device_type,
                        key,
                        index=entity.index,
                        key_index=entity.key_index,
                    ):
                        _LOGGER.debug(
                            'Skip deactivated %s with key "%s" (index: %s)',
                            entity_name,
                            description.ref_key or description.key,
                            index,
                        )
                        deactivated_unique_ids.add(entity.unique_id)
                        continue

                    entities.append(entity)

    _async_remove_deactivated_entities(entry, deactivated_unique_ids)
    async_add_entities(entities)


@callback
def _async_remove_deactivated_entities(entry: KebaKeEnergyConfigEntry, unique_ids: set[str], /) -> None:
    """Remove the entities of deactivated sensors that were created before from the entity registry."""
    entity_registry: er.EntityRegistry = er.async_get(entry.runtime_data.hass)

    for registry_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
        if registry_entry.unique_id in unique_ids:
            _LOGGER.debug("Remove entity %s of a deactivated sensor", registry_entry.entity_id)
            entity_registry.async_remove(registry_entry.entity_id)
