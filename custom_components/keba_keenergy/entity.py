"""Entity classes for the KEBA KeEnergy integration."""

from collections.abc import Mapping
from typing import Any
from typing import TYPE_CHECKING
from typing import cast

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.error import APIError

from .const import DOMAIN
from .const import MANUFACTURER
from .const import MANUFACTURER_MTEC
from .const import NAME
from .coordinator import KebaKeEnergyDataUpdateCoordinator

if TYPE_CHECKING:
    from keba_keenergy_api.endpoints import Value


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
    ) -> None:
        """Initialize the KEBA KeEnergy entity."""
        super().__init__(coordinator)
        self.entry: ConfigEntry = entry
        self.section_id: str = section_id
        self.index: int | None = index

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
    def is_heat_pump(self) -> bool:
        """Return True if the entity is part of a heat pump else False."""
        return self.section_id == SectionPrefix.HEAT_PUMP

    @property
    def is_hot_water_tank(self) -> bool:
        """Return True if the entity is part of a hot water tank else False."""
        return self.section_id == SectionPrefix.HOT_WATER_TANK

    @property
    def device_name(self) -> str | None:
        """Return the device name and number."""
        _device_name: str | None = None

        if self.is_system_device:
            _device_name = f"{self.device_manufacturer} {NAME}"
        elif self.is_heat_circuit:
            data: list[Value] = cast("list[Value]", self.coordinator.data[self.section_id]["name"])
            _device_name = data[self.index or 0]["value"]
        elif self.is_heat_pump:
            _device_name = "Heat pump"
        elif self.is_hot_water_tank:  # pragma: no branch
            _device_name = "Hot water tank"

        # Add position number to device name if there is more than one device
        # e.g. hot water tank, heat circuit or heat pump.
        if _device_name and self.position is not None:
            _device_name = f"{_device_name} ({self.position})"

        return _device_name

    @property
    def device_identifier(self) -> str:
        """Return the device identifier."""
        _identifier: str = f"{self.entry.unique_id}_{DOMAIN if self.is_system_device else self.section_id}"

        # Add position number to identifier if there is more than one device
        # e.g. hot water tank, heat circuit or heat pump.
        if self.position is not None:
            _identifier = f"{_identifier}_{self.position}"

        return _identifier

    @property
    def device_manufacturer(self) -> str | None:
        """Return the device manufacturer."""
        _manufacturer: str | None = None

        if self.is_system_device:
            _manufacturer = MANUFACTURER
        elif self.is_heat_pump and self.coordinator.device_name.endswith("MTec"):
            _manufacturer = MANUFACTURER_MTEC

        return _manufacturer

    @property
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

    @property
    def _translation_key(self) -> str | None:
        translation_key: str | None = None

        if self.is_heat_circuit:
            translation_key = "heat_circuit"
        elif self.is_heat_pump:
            translation_key = "heat_pump"
        elif self.is_hot_water_tank:
            translation_key = "hot_water_tank"

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
            "sw_version": (self.coordinator.device_sw_version if self.is_system_device else None),
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

    async def _async_write_data(self, section: Section, value: Any, device_numbers: int) -> None:
        """Write data to the KEBA KeEnergy API."""
        try:
            _current_index: int = self.index or 0

            await self.coordinator.api.write_data(
                request={
                    section: [value if index == _current_index else None for index in range(device_numbers)],
                },
            )
        except (APIError, ClientError) as error:
            msg: str = f"Failed to update {self.entity_id} to {value}: {error}"
            raise HomeAssistantError(msg) from error

        await self.coordinator.async_refresh()

    def get_attribute(self, key: str, attr: str) -> str:
        """Get extra attribute from the API by key."""
        data: list[Value] = cast("list[Value]", self.coordinator.data[self.section_id][key])
        return str(data[self.index or 0]["attributes"][attr])

    def get_value(self, key: str) -> Any:
        """Get value from the API by key."""
        data: list[Value] = cast("list[Value]", self.coordinator.data[self.section_id][key])
        return data[self.index or 0]["value"]
