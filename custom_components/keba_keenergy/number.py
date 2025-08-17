"""Support for the KEBA KeEnergy numbers."""

import logging

from keba_keenergy_api.constants import (
    HeatCircuit,
    HotWaterTank,
    Section,
    SectionPrefix,
)

from homeassistant.components.number import (
    DOMAIN as NUMBER_DOMAIN,
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyEntity

_LOGGER = logging.getLogger(__name__)


NUMBER_TYPES: dict[str, tuple[NumberEntityDescription, ...]] = {
    SectionPrefix.HEAT_CIRCUIT: (
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="day_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="day_temperature",
        ),
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="night_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="night_temperature",
        ),
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="holiday_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="holiday_temperature",
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="min_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="min_temperature",
            icon="mdi:thermometer-chevron-down",
        ),
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="max_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="max_temperature",
            icon="mdi:thermometer-chevron-up",
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up KEBA KeEnergy numbers from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    numbers: list[KebaKeEnergyNumberEntity] = []

    # Loop over all device data and add an index to the sensor
    # if there is more than one device of the same type
    # e.g. hot water tank, heat circuit or heat pump.
    for section_id, section_data in coordinator.data.items():
        for description in NUMBER_TYPES.get(section_id, {}):
            for key, values in section_data.items():
                if key == description.key:
                    device_numbers: int = len(values) if isinstance(values, list) else 1
                    for index in range(device_numbers):
                        numbers.append(
                            KebaKeEnergyNumberEntity(
                                coordinator=coordinator,
                                description=description,
                                entry=entry,
                                section_id=section_id,
                                index=index if device_numbers > 1 else None,
                            )
                        )

    async_add_entities(numbers)


class KebaKeEnergyNumberEntity(KebaKeEnergyEntity, NumberEntity):
    """KEBA KeEnergy number entity."""

    _attr_native_step: float = 0.5

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: NumberEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, entry, section_id, index)
        self.entity_description: NumberEntityDescription = description

        self._attr_unique_id = f"{entry.unique_id}_{section_id}_{description.key}"
        if self.position is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.position}"

        self.entity_id = f"{NUMBER_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def native_min_value(self) -> float:
        """Return the maximum value."""
        return float(
            self.coordinator.data[self.section_id][self.entity_description.key][
                self.index or 0
            ]["attributes"]["lower_limit"]
        )

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return float(
            self.coordinator.data[self.section_id][self.entity_description.key][
                self.index or 0
            ]["attributes"]["upper_limit"]
        )

    @property
    def native_value(self) -> float:
        """Return the state of the number."""
        return float(
            self.coordinator.data[self.section_id][self.entity_description.key][
                self.index or 0
            ]["value"]
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        section: Section | None = None
        device_numbers: int | None = None

        if self.section_id == SectionPrefix.HEAT_CIRCUIT:
            section = HeatCircuit[self.entity_description.key.upper()]
            device_numbers = self.coordinator.heat_circuit_numbers
        elif self.section_id == SectionPrefix.HOT_WATER_TANK:
            section = HotWaterTank[self.entity_description.key.upper()]
            device_numbers = self.coordinator.hot_water_tank_numbers

        if section and device_numbers:
            await self._async_update_data(
                section=section,
                value=value,
                device_numbers=device_numbers,
            )
