"""Support for the KEBA KeEnergy switches."""

import logging
from typing import Any
from typing import cast

from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.switch.const import DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyExtendedEntity

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
    """Set up KEBA KeEnergy switches from a config entry."""
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
                            coordinator,
                            description=description,
                            entry=entry,
                            section_id=section_id,
                            index=index if device_numbers > 1 else None,
                        )
                        for index in range(device_numbers)
                    ]

    async_add_entities(numbers)


_LOGGER = logging.getLogger(__name__)


class KebaKeEnergySwitchEntity(KebaKeEnergyExtendedEntity, SwitchEntity):
    """KEBA KeEnergy switch entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: SwitchEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: SwitchEntityDescription = description
        super().__init__(coordinator, entry=entry, section_id=section_id, index=index)
        self.entity_id: str = f"{SWITCH_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return cast("bool", (self.get_value(self.entity_description.key) == "on"))

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self._async_write_data(
            0,
            section=self.section,
            device_numbers=self.device_numbers,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self._async_write_data(
            1,
            section=self.section,
            device_numbers=self.device_numbers,
        )
