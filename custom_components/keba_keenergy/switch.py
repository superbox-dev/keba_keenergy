"""Support for the KEBA KeEnergy numbers."""

import logging
from typing import Any
from typing import TYPE_CHECKING
from typing import cast

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from keba_keenergy_api.constants import HeatPump
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyEntity

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)


SWITCH_TYPES: dict[str, tuple[SwitchEntityDescription, ...]] = {
    SectionPrefix.HEAT_PUMP: (
        SwitchEntityDescription(
            device_class=SwitchDeviceClass.SWITCH,
            key="compressor_use_night_speed",
            translation_key="compressor_use_night_speed",
        ),
    ),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up KEBA KeEnergy numbers from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    numbers: list[KebaKeEnergySwitchEntity] = []

    # Loop over all device data and add an index to the sensor
    # if there is more than one device of the same type
    # e.g. hot water tank, heat circuit or heat pump.
    for section_id, section_data in coordinator.data.items():
        for description in SWITCH_TYPES.get(section_id, {}):
            for key, values in section_data.items():
                if key == description.key:
                    device_numbers: int = len(values) if isinstance(values, list) else 1
                    numbers += [
                        KebaKeEnergySwitchEntity(
                            coordinator=coordinator,
                            description=description,
                            entry=entry,
                            section_id=section_id,
                            index=index if device_numbers > 1 else None,
                        )
                        for index in range(device_numbers)
                    ]

    async_add_entities(numbers)


_LOGGER = logging.getLogger(__name__)


class KebaKeEnergySwitchEntity(KebaKeEnergyEntity, SwitchEntity):
    """KEBA KeEnergy switch entity."""

    _attr_native_step: float = 0.5

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: SwitchEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, entry, section_id, index)
        self.entity_description: SwitchEntityDescription = description

        self._attr_unique_id = f"{entry.unique_id}_{section_id}_{description.key}"
        if self.position is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.position}"

        self.entity_id = f"{SWITCH_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

        self.section: Section | None = None
        self.device_numbers: int | None = None

        if self.section_id == SectionPrefix.HEAT_PUMP:
            self.section = HeatPump[self.entity_description.key.upper()]
            self.device_numbers = self.coordinator.heat_pump_numbers

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return cast("bool", (self.get_value(self.entity_description.key) == "on"))

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self._async_write_data(
            section=self.section,
            value=0,
            device_numbers=self.device_numbers,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self._async_write_data(
            section=self.section,
            value=1,
            device_numbers=self.device_numbers,
        )
