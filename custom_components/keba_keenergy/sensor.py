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
from homeassistant.const import EntityCategory
from homeassistant.const import PERCENTAGE
from homeassistant.const import STATE_OFF
from homeassistant.const import UnitOfEnergy
from homeassistant.const import UnitOfInformation
from homeassistant.const import UnitOfPower
from homeassistant.const import UnitOfPressure
from homeassistant.const import UnitOfTemperature
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from keba_keenergy_api.constants import BufferTankOperatingMode
from keba_keenergy_api.constants import ExternalHeatSourceOperatingMode
from keba_keenergy_api.constants import HeatCircuitHeatRequest
from keba_keenergy_api.constants import HeatCircuitOperatingMode
from keba_keenergy_api.constants import HeatPumpState
from keba_keenergy_api.constants import HeatPumpSubState
from keba_keenergy_api.constants import HotWaterTankOperatingMode
from keba_keenergy_api.constants import SectionPrefix
from keba_keenergy_api.constants import SystemOperatingMode

from .const import DOMAIN
from .coordinator import KebaKeEnergyDataUpdateCoordinator
from .entity import KebaKeEnergyExtendedEntity

if TYPE_CHECKING:
    from keba_keenergy_api.endpoints import Value


_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class KebaKeEnergySensorEntityDescriptionMixin:
    """Required values for KEBA KeEnergy sensors."""

    key_index: int | None
    value: Callable[[str | int | float], str | int | float]


@dataclass(frozen=True)
class KebaKeEnergySensorEntityDescription(
    SensorEntityDescription,
    KebaKeEnergySensorEntityDescriptionMixin,
):
    """Class describing KEBA KeEnergy sensor entities."""


SENSOR_TYPES: dict[str, tuple[KebaKeEnergySensorEntityDescription, ...]] = {
    SectionPrefix.SYSTEM: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="outdoor_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="outdoor_temperature",
            icon="mdi:sun-thermometer",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            key_index=None,
            options=[_.name.lower() for _ in SystemOperatingMode],
            translation_key="operating_mode_system",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="cpu_usage",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="cpu_usage",
            value=lambda data: cast("float", data) / 10,
        ),
        KebaKeEnergySensorEntityDescription(
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="webview_cpu_usage",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="webview_cpu_usage",
            value=lambda data: cast("float", data) / 10,
        ),
        KebaKeEnergySensorEntityDescription(
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="webserver_cpu_usage",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="webserver_cpu_usage",
            value=lambda data: cast("float", data) / 10,
        ),
        KebaKeEnergySensorEntityDescription(
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="control_cpu_usage",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="control_cpu_usage",
            value=lambda data: cast("float", data) / 10,
        ),
        KebaKeEnergySensorEntityDescription(
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="ram_usage",
            key_index=None,
            native_unit_of_measurement=UnitOfInformation.KILOBYTES,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="ram_usage",
            value=lambda data: cast("int", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            key="free_ram",
            key_index=None,
            native_unit_of_measurement=UnitOfInformation.KILOBYTES,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="free_ram",
            value=lambda data: cast("int", data),
        ),
    ),
    SectionPrefix.HEAT_CIRCUIT: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="room_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="room_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.HUMIDITY,
            entity_registry_enabled_default=False,
            key="room_humidity",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="room_humidity",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="dew_point",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="dew_point",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="flow_temperature_setpoint",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="flow_temperature_setpoint",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="flow_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="flow_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="return_flow_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="return_flow_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_day",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_day",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="heating_limit_day",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_limit_day",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_night",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_night",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="heating_limit_night",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_limit_night",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_away",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_away",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature_offset",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_room_temperature_offset",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            key_index=None,
            options=[_.name.lower() for _ in HeatCircuitOperatingMode],
            translation_key="operating_mode_heat_circuit",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="heat_request",
            key_index=None,
            options=[_.name.lower() for _ in HeatCircuitHeatRequest],
            translation_key="heat_request",
            icon="mdi:fire",
            value=lambda data: cast("str", data),
        ),
    ),
    SectionPrefix.SOLAR_CIRCUIT: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="source_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="source_temperature",
            icon="mdi:sun-thermometer",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            key="pump_1",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="solar_circuit_pump_1",
            icon="mdi:speedometer",
            value=lambda data: cast("float", data * 100),
        ),
        KebaKeEnergySensorEntityDescription(
            key="pump_2",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="solar_circuit_pump_2",
            icon="mdi:speedometer",
            value=lambda data: cast("float", data * 100),
        ),
        KebaKeEnergySensorEntityDescription(
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
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
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
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
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
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
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
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="heating_energy",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="heating_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="daily_energy",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="daily_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="actual_power",
            key_index=None,
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="actual_power",
            value=lambda data: cast("float", data),
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="state",
            key_index=None,
            options=[_.name.lower() for _ in HeatPumpState],
            translation_key="state",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="sub_state",
            key_index=None,
            options=[_.name.lower() for _ in HeatPumpSubState],
            translation_key="sub_state",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            key="circulation_pump",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="circulation_pump",
            icon="mdi:heat-pump",
            value=lambda data: cast("float", data * 100),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="flow_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="flow_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="return_flow_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="return_flow_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="source_input_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="source_input_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="source_output_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="source_output_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="compressor_input_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor_input_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="compressor_output_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor_output_temperature",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="compressor",
            key_index=None,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor",
            value=lambda data: cast("float", data * 100),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.PRESSURE,
            entity_registry_enabled_default=False,
            key="high_pressure",
            key_index=None,
            native_unit_of_measurement=UnitOfPressure.BAR,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="high_pressure",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.PRESSURE,
            entity_registry_enabled_default=False,
            key="low_pressure",
            key_index=None,
            native_unit_of_measurement=UnitOfPressure.BAR,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="low_pressure",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="compressor_power",
            key_index=None,
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="compressor_power",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="heating_power",
            key_index=None,
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_power",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.POWER,
            entity_registry_enabled_default=False,
            key="hot_water_power",
            key_index=None,
            native_unit_of_measurement=UnitOfPower.WATT,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="hot_water_power",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="cop",
            key_index=None,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="cop",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="heating_energy",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="heating_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="heating_energy_consumption",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="heating_energy_consumption",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="heating_spf",
            key_index=None,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="heating_spf",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="cooling_energy",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="cooling_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="cooling_energy_consumption",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="cooling_energy_consumption",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="cooling_spf",
            key_index=None,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="cooling_spf",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="hot_water_energy",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="hot_water_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="hot_water_energy_consumption",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="hot_water_energy_consumption",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="hot_water_spf",
            key_index=None,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="hot_water_spf",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="total_thermal_energy",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="total_thermal_energy",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENERGY,
            entity_registry_enabled_default=False,
            key="total_energy_consumption",
            key_index=None,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL,
            translation_key="total_energy_consumption",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="total_spf",
            key_index=None,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="total_spf",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            key="operating_time",
            key_index=None,
            native_unit_of_measurement=UnitOfTime.HOURS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="operating_hours",
            value=lambda data: round(int(data) / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="max_runtime",
            key_index=None,
            native_unit_of_measurement=UnitOfTime.HOURS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="max_runtime",
            value=lambda data: round(int(data) / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="activation_counter",
            key_index=None,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="activation_counter",
            value=lambda data: cast("int", data),
        ),
    ),
    SectionPrefix.BUFFER_TANK: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_top_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_top_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-water",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_bottom_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_bottom_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-water",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            key_index=None,
            options=[_.name.lower() for _ in BufferTankOperatingMode],
            translation_key="operating_mode_buffer_tank",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="standby_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-chevron-up",
            value=lambda data: cast("float", data),
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="current_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="current_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-water",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            key_index=None,
            options=[_.name.lower() for _ in HotWaterTankOperatingMode],
            translation_key="operating_mode_hot_water_tank",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="standby_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="standby_temperature",
            icon="mdi:thermometer-chevron-down",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            entity_registry_enabled_default=False,
            key="fresh_water_module_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="fresh_water_module_temperature",
            icon="mdi:thermometer-water",
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": "",
            },
            icon="mdi:thermometer-chevron-up",
            value=lambda data: cast("float", data),
        ),
    ),
    SectionPrefix.EXTERNAL_HEAT_SOURCE: (
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.ENUM,
            key="operating_mode",
            key_index=None,
            options=[_.name.lower() for _ in ExternalHeatSourceOperatingMode],
            translation_key="operating_mode_external_heat_source",
            value=lambda data: cast("str", data),
        ),
        KebaKeEnergySensorEntityDescription(
            device_class=SensorDeviceClass.TEMPERATURE,
            key="target_temperature",
            key_index=None,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="target_temperature",
            translation_placeholders={
                "counter": "",
            },
            value=lambda data: cast("float", data),
        ),
        KebaKeEnergySensorEntityDescription(
            key="operating_time",
            key_index=None,
            native_unit_of_measurement=UnitOfTime.HOURS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="operating_hours",
            value=lambda data: round(int(data) / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="max_runtime",
            key_index=None,
            native_unit_of_measurement=UnitOfTime.HOURS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="max_runtime",
            value=lambda data: round(int(data) / 3600, 2),
        ),
        KebaKeEnergySensorEntityDescription(
            entity_registry_enabled_default=False,
            key="activation_counter",
            key_index=None,
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="activation_counter",
            value=lambda data: cast("int", data),
        ),
    ),
    # SectionPrefix.PHOTOVOLTAIC: (
    #     KebaKeEnergySensorEntityDescription(
    #         device_class=SensorDeviceClass.POWER,
    #         key="excess_power",
    #         key_index=None,
    #         native_unit_of_measurement=UnitOfPower.WATT,
    #         state_class=SensorStateClass.MEASUREMENT,
    #         translation_key="pv_excess_power",
    #         value=lambda data: cast("float", data),
    #     ),
    #     KebaKeEnergySensorEntityDescription(
    #         device_class=SensorDeviceClass.ENERGY,
    #         key="daily_energy",
    #         key_index=None,
    #         native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    #         state_class=SensorStateClass.TOTAL,
    #         translation_key="daily_energy",
    #         value=lambda data: cast("float", data),
    #     ),
    #     KebaKeEnergySensorEntityDescription(
    #         device_class=SensorDeviceClass.ENERGY,
    #         key="total_energy",
    #         key_index=None,
    #         native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    #         state_class=SensorStateClass.TOTAL_INCREASING,
    #         translation_key="pv_total_energy",
    #         value=lambda data: cast("float", data),
    #     ),
    # ),
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
    # e.g. buffer tank, hot water tank, heat circuit, solar circuit or heat pump.

    for section_id, section_data in coordinator.data.items():
        if section_id == SectionPrefix.PHOTOVOLTAIC and coordinator.has_photovoltaics() == STATE_OFF:
            continue

        for description in SENSOR_TYPES.get(section_id, {}):
            for key, values in section_data.items():
                if key == description.key:
                    device_numbers: int = len(values) if isinstance(values, list) else 1
                    sensors += [
                        KebaKeEnergySensorEntity(
                            coordinator,
                            description=description,
                            entry=entry,
                            section_id=section_id,
                            index=index if device_numbers > 1 else None,
                        )
                        for index in range(device_numbers)
                    ]
    async_add_entities(sensors)


class KebaKeEnergySensorEntity(KebaKeEnergyExtendedEntity, SensorEntity):
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
        self.entity_description: KebaKeEnergySensorEntityDescription = description

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
        data: list[list[Value]] | list[Value] | Value | None = self.coordinator.data[self.section_id].get(
            self.entity_description.key,
            None,
        )
        value: str | int | float | None = None

        if isinstance(data, list):
            data = data[self.index or 0]

        if isinstance(data, list) and self.key_index is not None:
            data = data[self.key_index]

        if isinstance(data, dict):
            value = self.entity_description.value(data["value"])

        return value
