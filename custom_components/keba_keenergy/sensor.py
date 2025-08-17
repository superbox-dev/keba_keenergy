"""Support for the KEBA KeEnergy sensors."""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING
from typing import cast

from keba_keenergy_api.constants import SectionPrefix

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import KebaKeEnergyDataUpdateCoordinator
from .const import DOMAIN
from .entity import KebaKeEnergyEntity

if TYPE_CHECKING:
    from keba_keenergy_api.endpoints import Value


_LOGGER = logging.getLogger(__name__)


@dataclass
class KebaKeEnergySensorEntityDescriptionMixin:
    """Required values for KEBA KeEnergy sensors."""

    value: Callable[[str | int | float], str | int | float]


@dataclass
class KebaKeEnergySensorEntityDescription(
    SensorEntityDescription,
    KebaKeEnergySensorEntityDescriptionMixin,
):
    """Class describing KEBA KeEnergy sensor entities."""


SENSOR_TYPES: dict[str, tuple[KebaKeEnergySensorEntityDescription, ...]] = {
    SectionPrefix.HEAT_CIRCUIT: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="day_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="day_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="day_temperature_threshold",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="day_temperature_threshold",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="night_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="night_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="night_temperature_threshold",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="night_temperature_threshold",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="holiday_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="holiday_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="temperature_offset",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="temperature_offset",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            options=["off", "auto", "day", "night", "holiday", "party"],
            translation_key="operating_mode",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="heat_request",
            options=["off", "on", "temporary_off", "outdoor_temperature_off"],
            translation_key="heat_request",
            icon="mdi:fire",
            value=lambda data: cast("str", data),
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="state",
            options=["standby", "flow", "auto_heat", "defrost", "auto_cool", "inflow"],
            translation_key="state",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="circulation_pump",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="circulation_pump",
            icon="mdi:heat-pump",
            value=lambda data: cast("float", data * 100),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="inflow_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="inflow_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="reflux_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="reflux_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="source_input_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="source_input_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="source_output_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="source_output_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="compressor_input_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor_input_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="compressor_output_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor_output_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="compressor",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor",
            value=lambda data: cast("float", data * 100),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.PRESSURE,
            entity_registry_enabled_default=False,
            key="high_pressure",
            native_unit_of_measurement=UnitOfPressure.BAR,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="high_pressure",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.PRESSURE,
            entity_registry_enabled_default=False,
            key="low_pressure",
            native_unit_of_measurement=UnitOfPressure.BAR,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="low_pressure",
            value=lambda data: cast("float", data),
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="temperature",
            icon="mdi:thermometer-water",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            options=["auto", "heat_up", "off", "on"],
            translation_key="operating_mode",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="min_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="min_temperature",
            icon="mdi:thermometer-chevron-down",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="max_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="max_temperature",
            icon="mdi:thermometer-chevron-up",
            value=lambda data: cast("float", data),
        ),
    ),
    SectionPrefix.SYSTEM: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="outdoor_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="outdoor_temperature",
            icon="mdi:sun-thermometer",
            value=lambda data: cast("float", data),
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy sensors from a config entry."""
    coordinator: KebaKeEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors: list[KebaKeEnergySensorEntity] = []

    # Loop over all device data and add an index to the sensor
    # if there is more than one device of the same type
    # e.g. hot water tank, heat circuit or heat pump.
    for section_id, section_data in coordinator.data.items():
        for description in SENSOR_TYPES.get(section_id, {}):
            for key, values in section_data.items():
                if key == description.key:
                    device_numbers: int = len(values) if isinstance(values, list) else 1
                    sensors += [
                        KebaKeEnergySensorEntity(
                            coordinator=coordinator,
                            description=description,
                            entry=entry,
                            section_id=section_id,
                            index=index if device_numbers > 1 else None,
                        )
                        for index in range(device_numbers)
                    ]

    async_add_entities(sensors)


class KebaKeEnergySensorEntity(KebaKeEnergyEntity, SensorEntity):
    """KEBA KeEnergy sensor entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: KebaKeEnergySensorEntityDescription,
        entry: ConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, entry, section_id, index)
        self.entity_description: KebaKeEnergySensorEntityDescription = description

        if section_id == SectionPrefix.SYSTEM:
            self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        else:
            self._attr_unique_id = f"{entry.unique_id}_{section_id}_{description.key}"

        if self.position is not None:
            self._attr_unique_id = f"{self._attr_unique_id}_{self.position}"

        self.entity_id = f"{SENSOR_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        data: list[Value] | Value = self.coordinator.data[self.section_id][self.entity_description.key]

        if isinstance(data, list):
            data = data[self.index or 0]

        return self.entity_description.value(data["value"])
