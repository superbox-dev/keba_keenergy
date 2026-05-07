"""Support for the KEBA KeEnergy sensors."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from typing import Final
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import cast

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import EntityCategory
from homeassistant.const import PERCENTAGE
from homeassistant.const import UnitOfEnergy
from homeassistant.const import UnitOfInformation
from homeassistant.const import UnitOfPower
from homeassistant.const import UnitOfPressure
from homeassistant.const import UnitOfTemperature
from homeassistant.const import UnitOfTime
from keba_keenergy_api.constants import BoolEnum
from keba_keenergy_api.constants import BufferTankExcessEnergyMode
from keba_keenergy_api.constants import BufferTankOperatingMode
from keba_keenergy_api.constants import HeatCircuitCoolRequest
from keba_keenergy_api.constants import HeatCircuitExcessEnergyMode
from keba_keenergy_api.constants import HeatCircuitHeatRequest
from keba_keenergy_api.constants import HeatCircuitOperatingMode
from keba_keenergy_api.constants import HeatPumpState
from keba_keenergy_api.constants import HeatPumpSubState
from keba_keenergy_api.constants import HotWaterTankExcessEnergyMode
from keba_keenergy_api.constants import HotWaterTankOperatingMode
from keba_keenergy_api.constants import MixerSwitchValvePosition
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import SwitchValvePosition
from keba_keenergy_api.constants import SystemOperatingMode

from .const import DOMAIN
from .entity import KebaKeEnergyEntity
from .entity import KebaKeEnergyEntityDescriptionMixin
from .entity import _async_setup_entities

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType
    from keba_keenergy_api.endpoints import Value
    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator

T = TypeVar("T")


PARALLEL_UPDATES: Final[int] = 0
_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class KebaKeEnergySensorEntityDescription[T](
    SensorEntityDescription,
    KebaKeEnergyEntityDescriptionMixin,
):
    """Class describing KEBA KeEnergy sensor entities."""

    value: Callable[[T], StateType] = lambda data: cast("StateType", data)
    attributes: Callable[[Mapping[str, Any]], Mapping[str, Any]] = lambda data: data


class KebaKeEnergySensorEntity(KebaKeEnergyEntity, SensorEntity):
    """KEBA KeEnergy sensor entity."""

    def __init__(
        self,
        coordinator: KebaKeEnergyDataUpdateCoordinator,
        description: KebaKeEnergySensorEntityDescription[StateType],
        entry: KebaKeEnergyConfigEntry,
        section_id: str,
        index: int | None,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: KebaKeEnergySensorEntityDescription[StateType] = description

        super().__init__(
            coordinator,
            entry=entry,
            section_id=section_id,
            index=index,
            key_index=self.entity_description.key_index,
        )

        self.entity_id: str = f"{SENSOR_DOMAIN}.{DOMAIN}_{self._attr_unique_id}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value(
            self.get_value(self.entity_description.new_key or self.entity_description.key),
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes."""
        entity_data: Value | None = self.get_entity_data(self.entity_description.new_key or self.entity_description.key)
        attributes: Mapping[str, Any] = {}

        if isinstance(entity_data, dict):
            attributes = entity_data.get("attributes", {})

        return self.entity_description.attributes(attributes)


SENSOR_TYPES: dict[str, tuple[KebaKeEnergySensorEntityDescription[Any], ...]] = {
    SectionPrefix.SYSTEM: (
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="outdoor_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="outdoor_temperature",
            value=lambda data: data,
        ),
        KebaKeEnergySensorEntityDescription[str](
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            options=[_.name.lower() for _ in SystemOperatingMode],
            translation_key="system_operating_mode",
            value=lambda data: data,
        ),
        KebaKeEnergySensorEntityDescription[float](
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="cpu_usage",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="cpu_usage",
            value=lambda data: data / 10,
        ),
        KebaKeEnergySensorEntityDescription[float](
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="webview_cpu_usage",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="webview_cpu_usage",
            value=lambda data: data / 10,
        ),
        KebaKeEnergySensorEntityDescription[float](
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="webserver_cpu_usage",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="webserver_cpu_usage",
            value=lambda data: data / 10,
        ),
        KebaKeEnergySensorEntityDescription[float](
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="control_cpu_usage",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="control_cpu_usage",
            value=lambda data: data / 10,
        ),
        KebaKeEnergySensorEntityDescription[int](
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="ram_usage",
            native_unit_of_measurement=UnitOfInformation.KILOBYTES,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="ram_usage",
            value=lambda data: data,
        ),
        KebaKeEnergySensorEntityDescription[int](
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="free_ram",
            native_unit_of_measurement=UnitOfInformation.KILOBYTES,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="free_ram",
            value=lambda data: data,
        ),
    ),
    SectionPrefix.HEAT_CIRCUIT: (
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_room_temperature(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="room_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="room_temperature",
            icon="mdi:home-thermometer",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_room_humidity(index=index),
            device_class=SensorDeviceClass.HUMIDITY,
            entity_registry_enabled_default=False,
            key="room_humidity",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="room_humidity",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.has_room_temperature(index=index)
                and coordinator.has_room_humidity(index=index)
            ),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="dew_point",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="dew_point",
            icon="mdi:home-thermometer",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="flow_temperature_setpoint",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="flow_temperature_setpoint",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_mixer(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="flow_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            new_key="mixer_flow_temperature",
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="mixer_flow_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_mixer(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="mixer_return_flow_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="mixer_return_flow_temperature",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, index: coordinator.has_mixer(index=index),
            device_class=SensorDeviceClass.ENUM,
            entity_registry_enabled_default=False,
            key="mixer_position",
            options=[_.name.lower() for _ in MixerSwitchValvePosition],
            translation_key="mixer_position",
            attributes=lambda attributes: {**attributes, "position_percent": attributes["raw_value"] * 100},
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_return_flow_temperature(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="return_flow_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="return_flow_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="selected_target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="selected_target_room_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_day",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_cooling_temperature_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_cooling_temperature_day",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="heating_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_limit_day",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="cooling_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="cooling_limit_day",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.is_heating_circuit(index=index)
                and coordinator.has_photovoltaics()
            ),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="excess_energy_heating_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_heating_limit_day",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.is_cooling_circuit(index=index)
                and coordinator.has_photovoltaics()
            ),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="excess_energy_cooling_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_cooling_limit_day",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.is_heating_circuit(index=index)
                and coordinator.has_photovoltaics()
            ),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="excess_energy_heating_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_heating_limit_day",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.is_cooling_circuit(index=index)
                and coordinator.has_photovoltaics()
            ),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="excess_energy_cooling_limit_day",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_cooling_limit_day",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_night",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_cooling_temperature_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_cooling_temperature_night",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="heating_limit_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_limit_night",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="cooling_limit_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="cooling_limit_night",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.is_heating_circuit(index=index)
                and coordinator.has_photovoltaics()
            ),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="excess_energy_heating_limit_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_heating_limit_night",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.is_cooling_circuit(index=index)
                and coordinator.has_photovoltaics()
            ),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="excess_energy_cooling_limit_night",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_cooling_limit_night",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_away",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_away",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_offset",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_offset",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.is_heating_circuit(index=index)
                and coordinator.has_photovoltaics()
            ),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="excess_energy_target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_target_temperature",
            icon="mdi:sun-thermometer",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.is_cooling_circuit(index=index)
                and coordinator.has_photovoltaics()
            ),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="excess_energy_target_cooling_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_target_cooling_temperature",
            icon="mdi:sun-thermometer",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.ENUM,
            key="excess_energy_mode",
            options=[_.name.lower() for _ in HeatCircuitExcessEnergyMode],
            translation_key="excess_energy_mode",
        ),
        KebaKeEnergySensorEntityDescription[str](
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            options=[_.name.lower() for _ in HeatCircuitOperatingMode],
            translation_key="heat_circuit_operating_mode",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            device_class=SensorDeviceClass.ENUM,
            key="heat_request",
            options=[_.name.lower() for _ in HeatCircuitHeatRequest],
            translation_key="heat_request",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            device_class=SensorDeviceClass.ENUM,
            entity_registry_enabled_default=False,
            key="cool_request",
            options=[_.name.lower() for _ in HeatCircuitCoolRequest],
            translation_key="cool_request",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, index: coordinator.is_heating_circuit(index=index),
            key="heating_curve",
            translation_key="heating_curve",
            icon="mdi:chart-bell-curve-cumulative",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, index: coordinator.is_cooling_circuit(index=index),
            key="cooling_curve",
            translation_key="cooling_curve",
            icon="mdi:chart-bell-curve-cumulative",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_pump(index=index),
            entity_registry_enabled_default=False,
            key="pump_speed",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="pump_speed",
            value=lambda data: data * 100,
        ),
    ),
    SectionPrefix.SOLAR_CIRCUIT: (
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="source_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="source_temperature",
            icon="mdi:sun-thermometer",
        ),
        KebaKeEnergySensorEntityDescription[float](
            key="pump_1",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="solar_circuit_pump_1",
            value=lambda data: data * 100,
        ),
        KebaKeEnergySensorEntityDescription[float](
            key="pump_2",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="solar_circuit_pump_2",
            value=lambda data: data * 100,
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_temperature",
            key_index=0,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_temperature",
            translation_placeholders={
                "counter": " 1",
            },
            icon="mdi:thermometer-water",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_temperature",
            key_index=1,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_temperature",
            translation_placeholders={
                "counter": " 2",
            },
            icon="mdi:thermometer-water",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            key_index=0,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": " 1",
            },
            icon="mdi:thermometer-water",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            key_index=1,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": " 2",
            },
            icon="mdi:thermometer-water",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="heating_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="heating_energy",
            value=lambda data: round(data / 3_600_000, 2),  # Convert Joule to kWh
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="daily_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="daily_energy",
            value=lambda data: round(data / 3_600_000, 2),  # Convert Joule to kWh
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="actual_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="actual_power",
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        KebaKeEnergySensorEntityDescription[str](
            device_class=SensorDeviceClass.ENUM,
            key="state",
            options=[_.name.lower() for _ in HeatPumpState],
            translation_key="state",
            icon="mdi:cog",
        ),
        KebaKeEnergySensorEntityDescription[str](
            device_class=SensorDeviceClass.ENUM,
            key="substate",
            options=[_.name.lower() for _ in HeatPumpSubState],
            translation_key="substate",
            icon="mdi:cog",
        ),
        KebaKeEnergySensorEntityDescription[float](
            key="circulation_pump",
            native_unit_of_measurement=PERCENTAGE,
            new_key="circulation_pump_speed",
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="circulation_pump_speed",
            value=lambda data: data * 100,
        ),
        KebaKeEnergySensorEntityDescription[float](
            key="source_pump_speed",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="source_pump_speed",
            value=lambda data: data * 100,
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="flow_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="flow_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="return_flow_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="return_flow_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="source_input_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="source_input_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="source_output_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="source_output_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="compressor_input_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor_input_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="compressor_output_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor_output_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="condenser_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="condenser_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="vaporizer_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="vaporizer_temperature",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_overheating",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_overheating",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_overheating",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_overheating",
        ),
        KebaKeEnergySensorEntityDescription[str](
            key="expansion_valve_position",
            translation_key="expansion_valve_position",
            suggested_display_precision=0,
        ),
        KebaKeEnergySensorEntityDescription[float](
            key="compressor",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor",
            value=lambda data: data * 100,
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.PRESSURE,
            key="high_pressure",
            native_unit_of_measurement=UnitOfPressure.BAR,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="high_pressure",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.PRESSURE,
            key="low_pressure",
            native_unit_of_measurement=UnitOfPressure.BAR,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="low_pressure",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index),
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="compressor_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor_power",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_heat_meter(index=index),
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="heating_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_power",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_heat_meter(index=index),
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="hot_water_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="hot_water_power",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index)
                and coordinator.has_heat_meter(index=index)
            ),
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="cop",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            translation_key="cop",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_heat_meter(index=index),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="heating_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="heating_energy",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="heating_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="heating_energy_consumption",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index)
                and coordinator.has_heat_meter(index=index)
            ),
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="heating_spf",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            translation_key="heating_spf",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_heat_meter(index=index),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="cooling_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="cooling_energy",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index)
                and (coordinator.has_active_cooling(index=index) or coordinator.has_passive_cooling(index=index))
            ),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="cooling_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="cooling_energy_consumption",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index)
                and coordinator.has_heat_meter(index=index)
            ),
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="cooling_spf",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            translation_key="cooling_spf",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(lambda coordinator, index: coordinator.has_heat_meter(index=index)),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="hot_water_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="hot_water_energy",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="hot_water_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="hot_water_energy_consumption",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index)
                and coordinator.has_heat_meter(index=index)
            ),
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="hot_water_spf",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            translation_key="hot_water_spf",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_heat_meter(index=index),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="total_thermal_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="total_thermal_energy",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="total_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="total_energy_consumption",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(
                lambda coordinator, index: coordinator.has_electrical_energy_meter(index=index)
                and (coordinator.has_heat_meter(index=index) or coordinator.has_heat_meter(index=index))
            ),
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="total_spf",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            translation_key="total_spf",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="excess_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="excess_energy_consumption",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="heating_excess_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="heating_excess_energy_consumption",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=(lambda coordinator, _: coordinator.has_photovoltaics()),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="cooling_excess_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="cooling_excess_energy_consumption",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="hot_water_excess_energy_consumption",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="hot_water_excess_energy_consumption",
        ),
        KebaKeEnergySensorEntityDescription[int](
            device_class=SensorDeviceClass.DURATION,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="operating_time",
            native_unit_of_measurement=UnitOfTime.HOURS,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="operating_time",
            value=lambda data: round(data / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription[int](
            device_class=SensorDeviceClass.DURATION,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="max_runtime",
            native_unit_of_measurement=UnitOfTime.HOURS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="max_runtime",
            value=lambda data: round(data / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription[int](
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="activation_counter",
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=0,
            translation_key="activation_counter",
        ),
        KebaKeEnergySensorEntityDescription[int](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.DURATION,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="excess_energy_operating_time",
            native_unit_of_measurement=UnitOfTime.HOURS,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="excess_energy_operating_time",
            value=lambda data: round(data / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription[int](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.DURATION,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="excess_energy_max_runtime",
            native_unit_of_measurement=UnitOfTime.HOURS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_max_runtime",
            value=lambda data: round(data / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription[int](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            entity_registry_enabled_default=False,
            entity_category=EntityCategory.DIAGNOSTIC,
            key="excess_energy_activation_counter",
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=0,
            translation_key="excess_energy_activation_counter",
        ),
    ),
    SectionPrefix.PASSIVE_COOLING: (
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_passive_cooling(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="temperature",
            icon="mdi:snowflake-thermometer",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, index: coordinator.has_passive_cooling(index=index),
            device_class=SensorDeviceClass.ENUM,
            key="switch_valve_position",
            options=[_.name.lower() for _ in SwitchValvePosition],
            translation_key="passive_cooling_valve_position",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_passive_cooling(index=index),
            key="circulation_pump_speed",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="circulation_pump_speed",
            value=lambda data: data * 100,
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_passive_cooling(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="mixer_flow_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="mixer_flow_temperature",
            icon="mdi:snowflake-thermometer",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_passive_cooling(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="mixer_target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="mixer_target_temperature",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, index: coordinator.has_passive_cooling(index=index),
            device_class=SensorDeviceClass.ENUM,
            key="mixer_position",
            options=[_.name.lower() for _ in MixerSwitchValvePosition],
            translation_key="mixer_position",
            attributes=lambda attributes: {**attributes, "position_percent": attributes["raw_value"] * 100},
        ),
    ),
    SectionPrefix.BUFFER_TANK: (
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_top_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_top_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-water",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_bottom_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_bottom_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-water",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="excess_energy_target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_target_temperature",
            icon="mdi:sun-thermometer",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.ENUM,
            key="excess_energy_mode",
            options=[_.name.lower() for _ in BufferTankExcessEnergyMode],
            translation_key="excess_energy_mode",
        ),
        KebaKeEnergySensorEntityDescription[str](
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            options=[_.name.lower() for _ in BufferTankOperatingMode],
            translation_key="buffer_tank_operating_mode",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="standby_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-chevron-up",
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-water",
        ),
        KebaKeEnergySensorEntityDescription[str](
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            options=[_.name.lower() for _ in HotWaterTankOperatingMode],
            translation_key="hot_water_tank_operating_mode",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="standby_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, index: coordinator.has_fresh_water_module(index=index),
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="fresh_water_module_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="fresh_water_module_temperature",
            icon="mdi:thermometer-water",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-chevron-up",
        ),
        KebaKeEnergySensorEntityDescription[float](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.TEMPERATURE,
            key="excess_energy_target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_target_temperature",
            icon="mdi:sun-thermometer",
        ),
        KebaKeEnergySensorEntityDescription[str](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.ENUM,
            key="excess_energy_mode",
            options=[_.name.lower() for _ in HotWaterTankExcessEnergyMode],
            translation_key="excess_energy_mode",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="circulation_return_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="circulation_return_temperature",
        ),
    ),
    SectionPrefix.EXTERNAL_HEAT_SOURCE: (
        KebaKeEnergySensorEntityDescription[str](
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            options=[_.name.lower() for _ in BoolEnum],
            translation_key="external_heat_source_operating_mode",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": "",
            },
        ),
        KebaKeEnergySensorEntityDescription[int](
            entity_category=EntityCategory.DIAGNOSTIC,
            key="operating_time",
            native_unit_of_measurement=UnitOfTime.HOURS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="operating_time",
            value=lambda data: round(data / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription[int](
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="max_runtime",
            native_unit_of_measurement=UnitOfTime.HOURS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="max_runtime",
            value=lambda data: round(data / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription[int](
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="activation_counter",
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=0,
            translation_key="activation_counter",
        ),
        KebaKeEnergySensorEntityDescription[int](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.DURATION,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="excess_energy_operating_time",
            native_unit_of_measurement=UnitOfTime.HOURS,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="excess_energy_operating_time",
            value=lambda data: round(data / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription[int](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            device_class=SensorDeviceClass.DURATION,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="excess_energy_max_runtime",
            native_unit_of_measurement=UnitOfTime.HOURS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_energy_max_runtime",
            value=lambda data: round(data / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription[int](
            condition=lambda coordinator, _: coordinator.has_photovoltaics(),
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="excess_energy_activation_counter",
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=0,
            translation_key="excess_energy_activation_counter",
        ),
    ),
    SectionPrefix.SWITCH_VALVE: (
        KebaKeEnergySensorEntityDescription[str](
            device_class=SensorDeviceClass.ENUM,
            key="position",
            options=[_.name.lower() for _ in SwitchValvePosition],
            translation_key="switch_valve_position",
        ),
    ),
    SectionPrefix.PHOTOVOLTAICS: (
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.POWER,
            key="excess_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="excess_power",
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.ENERGY,
            key="daily_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="daily_energy",
            value=lambda data: round(data / 3_600_000, 2),  # Convert Joule to kWh
        ),
        KebaKeEnergySensorEntityDescription[float](
            device_class=SensorDeviceClass.ENERGY,
            key="total_energy",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="total_energy",
            value=lambda data: round(data / 3_600_000, 2),  # Convert Joule to kWh
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy sensors from a config entry."""
    await _async_setup_entities(
        entry,
        async_add_entities,
        SENSOR_TYPES,
        KebaKeEnergySensorEntity,
        "sensor",
    )
