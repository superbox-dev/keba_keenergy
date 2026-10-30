# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Support for the KEBA KeEnergy selects."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Final

from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SelectEntity
from homeassistant.components.select import SelectEntityDescription
from homeassistant.const import EntityCategory
from keba_keenergy_api.enums import BufferTankOperatingMode
from keba_keenergy_api.enums import DHWTankOperatingMode
from keba_keenergy_api.enums import ExternalHeatSourceOperatingMode
from keba_keenergy_api.enums import HeatingCircuitOperatingMode
from keba_keenergy_api.enums import SolarCircuitOperatingMode
from keba_keenergy_api.enums import SystemOperatingMode

from .const import SectionPrefix
from .entity import KebaKeEnergyEntity
from .entity import KebaKeEnergyEntityDescription
from .entity import async_setup_entities
from .entity import is_cooling_circuit
from .entity import is_heating_circuit
from .legacy import get_member
from .legacy import get_state
from .legacy import get_states

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from keba_keenergy_api.models import Value
    from keba_keenergy_api.models import WriteValue

    from .coordinator import KebaKeEnergyConfigEntry


_LOGGER: Final = logging.getLogger(__name__)

PARALLEL_UPDATES: Final[int] = 0


@dataclass(frozen=True, kw_only=True)
class KebaKeEnergySelectEntityDescription(
    SelectEntityDescription,
    KebaKeEnergyEntityDescription,
):
    """Class describing KEBA KeEnergy select entities."""

    entity_class: type[KebaKeEnergySelectEntity]
    # The enum of the options, None for options that are written as they are (e.g. the names of the curves).
    option_enum: type[Enum] | None = None


class KebaKeEnergySelectEntity(KebaKeEnergyEntity, SelectEntity):
    """KEBA KeEnergy select entity."""

    entity_description: KebaKeEnergySelectEntityDescription
    _platform_domain: str = SELECT_DOMAIN

    @cached_property
    def options(self) -> list[str]:
        """Return the options of the entity description."""
        return self.entity_description.options or []

    @property
    def current_option(self) -> str | None:
        """Return the selected option, None if the value is missing."""
        value: Value | None = self.get_value(self._data_key)

        if isinstance(value, Enum):
            return get_state(value)

        return value if isinstance(value, str) else None

    async def async_select_option(self, option: str) -> None:
        """Select an option, written only if it changed."""
        if option != self.current_option:
            option_enum: type[Enum] | None = self.entity_description.option_enum
            value: WriteValue = option if option_enum is None else get_member(option_enum, option)
            await self._async_write_value(value, key=self._data_key)


class KebaKeEnergySystemOperatingModeSelectEntity(KebaKeEnergySelectEntity):
    """KEBA KeEnergy system operating mode select entity."""

    @cached_property
    def options(self) -> list[str]:
        """Return the options, the cooling modes only if any heat pump or heating circuit cools."""
        options: list[str] = super().options

        if self.coordinator.has_cooling_heat_pump() or self.coordinator.has_cooling_circuit():
            return [
                *options,
                get_state(SystemOperatingMode.AUTO_COOLING),
                get_state(SystemOperatingMode.AUTO),
            ]

        return options


class KebaKeEnergyHeatingCircuitOperatingModeSelectEntity(KebaKeEnergySelectEntity):
    """KEBA KeEnergy heating circuit operating mode select entity."""

    @cached_property
    def options(self) -> list[str]:
        """Return the options, the vacation mode only if the heating circuit heats."""
        options: list[str] = super().options

        if self.coordinator.is_heating_circuit(index=self.index):
            return [
                *options,
                get_state(HeatingCircuitOperatingMode.VACATION),
            ]

        return options


class KebaKeEnergyExternalHeatSourceOperatingModeSelectEntity(KebaKeEnergySelectEntity):
    """KEBA KeEnergy external heat source operating mode select entity."""

    @cached_property
    def options(self) -> list[str]:
        """Return the options, the flue mode only if the external heat source has emissions."""
        options: list[str] = super().options

        if self.coordinator.has_emissions(index=self.index):
            return [
                *options,
                get_state(ExternalHeatSourceOperatingMode.FLUE),
            ]

        return options


class KebaKeEnergyCurveSelectEntity(KebaKeEnergySelectEntity):
    """KEBA KeEnergy select entity of the heating or cooling curve of a heating circuit."""

    @property
    def options(self) -> list[str]:
        """Return the names of the curves, read with every update of the heating circuits."""
        return list(self.coordinator.curve_names)


SELECT_TYPES: Final[dict[SectionPrefix, tuple[KebaKeEnergySelectEntityDescription, ...]]] = {
    SectionPrefix.SYSTEM: (
        KebaKeEnergySelectEntityDescription(
            entity_class=KebaKeEnergySystemOperatingModeSelectEntity,
            entity_category=EntityCategory.CONFIG,
            key="operating_mode",
            option_enum=SystemOperatingMode,
            options=[
                get_state(SystemOperatingMode.STANDBY),
                get_state(SystemOperatingMode.SUMMER),
                get_state(SystemOperatingMode.AUTO_HEATING),
            ],
            translation_key="system_operating_mode",
        ),
    ),
    SectionPrefix.HEATING_CIRCUIT: (
        KebaKeEnergySelectEntityDescription(
            entity_class=KebaKeEnergyHeatingCircuitOperatingModeSelectEntity,
            entity_category=EntityCategory.CONFIG,
            key="operating_mode",
            option_enum=HeatingCircuitOperatingMode,
            options=[
                get_state(HeatingCircuitOperatingMode.OFF),
                get_state(HeatingCircuitOperatingMode.AUTO),
                get_state(HeatingCircuitOperatingMode.NORMAL),
                get_state(HeatingCircuitOperatingMode.REDUCED),
                get_state(HeatingCircuitOperatingMode.PARTY),
            ],
            translation_key="heating_circuit_operating_mode",
        ),
        KebaKeEnergySelectEntityDescription(
            condition=is_heating_circuit,
            entity_class=KebaKeEnergyCurveSelectEntity,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="heating_curve",
            translation_key="heating_curve",
        ),
        KebaKeEnergySelectEntityDescription(
            condition=is_cooling_circuit,
            entity_class=KebaKeEnergyCurveSelectEntity,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="cooling_curve",
            translation_key="cooling_curve",
        ),
    ),
    SectionPrefix.SOLAR_CIRCUIT: (
        KebaKeEnergySelectEntityDescription(
            entity_class=KebaKeEnergySelectEntity,
            entity_category=EntityCategory.CONFIG,
            key="operating_mode",
            option_enum=SolarCircuitOperatingMode,
            options=get_states(SolarCircuitOperatingMode),
            translation_key="solar_circuit_operating_mode",
        ),
    ),
    SectionPrefix.BUFFER_TANK: (
        KebaKeEnergySelectEntityDescription(
            entity_class=KebaKeEnergySelectEntity,
            entity_category=EntityCategory.CONFIG,
            key="operating_mode",
            option_enum=BufferTankOperatingMode,
            options=get_states(BufferTankOperatingMode),
            translation_key="buffer_tank_operating_mode",
        ),
    ),
    SectionPrefix.DHW_TANK: (
        KebaKeEnergySelectEntityDescription(
            entity_class=KebaKeEnergySelectEntity,
            entity_category=EntityCategory.CONFIG,
            key="operating_mode",
            option_enum=DHWTankOperatingMode,
            options=get_states(DHWTankOperatingMode),
            translation_key="dhw_tank_operating_mode",
        ),
    ),
    SectionPrefix.EXTERNAL_HEAT_SOURCE: (
        KebaKeEnergySelectEntityDescription(
            entity_class=KebaKeEnergyExternalHeatSourceOperatingModeSelectEntity,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="operating_mode",
            option_enum=ExternalHeatSourceOperatingMode,
            options=[
                get_state(ExternalHeatSourceOperatingMode.OFF),
                get_state(ExternalHeatSourceOperatingMode.ON),
            ],
            translation_key="external_heat_source_operating_mode",
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy selects from a config entry."""
    async_setup_entities(
        entry,
        async_add_entities,
        SELECT_TYPES,
        KebaKeEnergySelectEntity,
        "select",
    )
