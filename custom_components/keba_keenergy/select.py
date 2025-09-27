"""Support for the KEBA KeEnergy selects."""

import logging
from functools import cached_property

from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SelectEntity
from homeassistant.components.select import SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import SystemOperatingMode

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyExtendedEntity

_LOGGER = logging.getLogger(__name__)


SELECT_TYPES: dict[str, tuple[SelectEntityDescription, ...]] = {
    SectionPrefix.SYSTEM: (
        SelectEntityDescription(
            key="operating_mode",
            options=[
                SystemOperatingMode.STANDBY.name.lower(),
                SystemOperatingMode.SUMMER.name.lower(),
                SystemOperatingMode.AUTO_HEAT.name.lower(),
            ],
            translation_key="operating_mode_3",
        ),
    ),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up KEBA KeEnergy selects from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    numbers: list[KebaKeEnergySelectEntity] = []

    # Loop over all device data and add an index to the sensor
    # if there is more than one device of the same type
    # e.g. hot water tank, heat circuit or heat pump.
    for section_id, section_data in coordinator.data.items():
        for description in SELECT_TYPES.get(section_id, {}):
            for key, values in section_data.items():
                if key == description.key:
                    device_numbers: int = len(values) if isinstance(values, list) else 1
                    numbers += [
                        KebaKeEnergySelectEntity(
                            coordinator,
                            description=description,
                            entry=entry,
                            section_id=section_id,
                            index=index if device_numbers > 1 else None,
                        )
                        for index in range(device_numbers)
                    ]

    async_add_entities(numbers)


class KebaKeEnergySelectEntity(KebaKeEnergyExtendedEntity, SelectEntity):
    """KEBA KeEnergy select entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: SelectEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: SelectEntityDescription = description
        super().__init__(coordinator, entry=entry, section_id=section_id, index=index)
        self.entity_id: str = f"{SELECT_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @cached_property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        options: list [str] = self.entity_description.options or []

        if (
            self.is_system_device
            and self.entity_description.key == "operating_mode"
            and self.coordinator.has_passive_cooling(index=self.index or 0) == STATE_ON
        ):
            return [
                *options,
                SystemOperatingMode.AUTO_COOL.name.lower(),
                SystemOperatingMode.AUTO.name.lower(),
            ]

        return options

    @property
    def current_option(self) -> str | None:
        """Return current select option."""
        return str(self.get_value(self.entity_description.key))

    async def async_select_option(self, option: str) -> None:
        """Select new option."""
        await self._async_write_data(
            SystemOperatingMode[option.upper()].value,
            section=self.section,
            device_numbers=self.device_numbers,
        )
