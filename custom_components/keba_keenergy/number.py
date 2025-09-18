"""Support for the KEBA KeEnergy numbers."""

import logging
from typing import TYPE_CHECKING
from typing import cast

from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.number import NumberEntity
from homeassistant.components.number import NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from keba_keenergy_api.constants import HeatCircuit
from keba_keenergy_api.constants import HotWaterTank
from keba_keenergy_api.constants import Section
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyEntity

if TYPE_CHECKING:
    from keba_keenergy_api.endpoints import Value

_LOGGER = logging.getLogger(__name__)


NUMBER_TYPES: dict[str, tuple[NumberEntityDescription, ...]] = {
    SectionPrefix.HEAT_CIRCUIT: (
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="target_temperature_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="target_temperature_day",
        ),
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="target_temperature_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="target_temperature_night",
        ),
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="target_temperature_away",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="target_temperature_away",
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="standby_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
        ),
        NumberEntityDescription(
            device_class=NumberDeviceClass.TEMPERATURE,
            key="target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="target_temperature",
            icon="mdi:thermometer-chevron-up",
        ),
    ),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
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
                    numbers += [
                        KebaKeEnergyNumberEntity(
                            coordinator=coordinator,
                            description=description,
                            entry=entry,
                            section_id=section_id,
                            index=index if device_numbers > 1 else None,
                        )
                        for index in range(device_numbers)
                    ]

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
        data: list[Value] = cast("list[Value]", self.coordinator.data[self.section_id][self.entity_description.key])
        return float(data[self.index or 0]["attributes"]["lower_limit"])

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        data: list[Value] = cast("list[Value]", self.coordinator.data[self.section_id][self.entity_description.key])
        return float(data[self.index or 0]["attributes"]["upper_limit"])

    @property
    def native_value(self) -> float:
        """Return the state of the number."""
        data: list[Value] = cast("list[Value]", self.coordinator.data[self.section_id][self.entity_description.key])
        return float(data[self.index or 0]["value"])

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        section: Section | None = None
        device_numbers: int | None = None

        if self.section_id == SectionPrefix.HEAT_CIRCUIT:
            section = HeatCircuit[self.entity_description.key.upper()]
            device_numbers = self.coordinator.heat_circuit_numbers
        elif self.section_id == SectionPrefix.HOT_WATER_TANK:  # pragma: no branch
            section = HotWaterTank[self.entity_description.key.upper()]
            device_numbers = self.coordinator.hot_water_tank_numbers

        if section and device_numbers:  # pragma: no branch
            await self._async_write_data(
                section=section,
                value=value,
                device_numbers=device_numbers,
            )
