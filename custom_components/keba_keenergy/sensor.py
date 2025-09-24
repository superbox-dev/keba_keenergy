"""Support for the KEBA KeEnergy sensors."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import cast

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.sensor import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.const import UnitOfEnergy
from homeassistant.const import UnitOfPower
from homeassistant.const import UnitOfPressure
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from keba_keenergy_api.constants import SectionPrefix

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyEntity

if TYPE_CHECKING:
    from keba_keenergy_api.endpoints import Value


_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class KebaKeEnergySensorEntityDescriptionMixin:
    """Required values for KEBA KeEnergy sensors."""

    value: Callable[[str | int | float], str | int | float]


@dataclass(frozen=True)
class KebaKeEnergySensorEntityDescription(
    SensorEntityDescription,
    KebaKeEnergySensorEntityDescriptionMixin,
):
    """Class describing KEBA KeEnergy sensor entities."""


SENSOR_TYPES: dict[str, tuple[KebaKeEnergySensorEntityDescription, ...]] = {
    SectionPrefix.HEAT_CIRCUIT: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="room_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="room_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.HUMIDITY,
            key="room_humidity",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="room_humidity",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="dew_point",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="dew_point",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="flow_temperature_setpoint",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="flow_temperature_setpoint",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_day",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="heating_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_limit_day",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_night",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="heating_limit_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_limit_night",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_away",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_away",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_offset",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_offset",
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
            options=["off", "on", "temporary_off", "room_off", "outdoor_off"],
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
            key="flow_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="flow_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="return_flow_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="return_flow_temperature",
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
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="compressor_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor_power",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="heating_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_power",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="hot_water_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="hot_water_power",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="cop",
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="cop",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="heating_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="heating_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="heating_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="heating_energy_consumption",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="heating_spf",
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_spf",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="cooling_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="cooling_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="cooling_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="cooling_energy_consumption",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="cooling_spf",
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="cooling_spf",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="hot_water_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="hot_water_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="hot_water_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="hot_water_energy_consumption",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="hot_water_spf",
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="hot_water_spf",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="total_thermal_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="total_thermal_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="total_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="total_energy_consumption",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="total_spf",
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="total_spf",
            value=lambda data: cast("float", data),
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_temperature",
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
            key="standby_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="fresh_water_module_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="fresh_water_module_temperature",
            icon="mdi:thermometer-water",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_temperature",
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
