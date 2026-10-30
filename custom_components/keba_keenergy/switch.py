# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Support for the KEBA KeEnergy switches."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Final

from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.switch.const import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import EntityCategory

from .const import SectionPrefix
from .entity import KebaKeEnergyEntity
from .entity import KebaKeEnergyEntityDescription
from .entity import async_setup_entities
from .entity import has_photovoltaics
from .entity import is_cooling_only_circuit
from .entity import is_heating_circuit

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import KebaKeEnergyConfigEntry

_LOGGER: Final = logging.getLogger(__name__)

PARALLEL_UPDATES: Final[int] = 0


@dataclass(frozen=True, kw_only=True)
class KebaKeEnergySwitchEntityDescription(
    SwitchEntityDescription,
    KebaKeEnergyEntityDescription,
):
    """Class describing KEBA KeEnergy switch entities."""


class KebaKeEnergySwitchEntity(KebaKeEnergyEntity, SwitchEntity):
    """KEBA KeEnergy switch entity."""

    entity_description: KebaKeEnergySwitchEntityDescription
    _platform_domain: str = SWITCH_DOMAIN

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        return self.get_typed_value(self._data_key, bool)

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch off."""
        if self.is_on:
            value: bool = False
            await self._async_write_data(value, key=self._data_key)

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Turn the switch on."""
        if not self.is_on:
            value: bool = True
            await self._async_write_data(value, key=self._data_key)


SWITCH_TYPES: Final[dict[SectionPrefix, tuple[KebaKeEnergySwitchEntityDescription, ...]]] = {
    SectionPrefix.HEAT_CIRCUIT: (
        KebaKeEnergySwitchEntityDescription(
            condition=has_photovoltaics,
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="use_excess_energy",
            translation_key="use_excess_energy",
        ),
        KebaKeEnergySwitchEntityDescription(
            condition=is_heating_circuit,
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="use_heating_curve",
            translation_key="use_heating_curve",
        ),
        # Heating and cooling circuits have one curve setting, so only cooling circuits get the cooling curve switch.
        # TODO: Use the key `use_curve_table` without `ref_key` when the unique IDs are migrated to the keys of
        # `keba_keenergy_api` 3.0.
        KebaKeEnergySwitchEntityDescription(
            condition=is_cooling_only_circuit,
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="use_heating_curve",
            ref_key="use_cooling_curve",
            translation_key="use_cooling_curve",
        ),
    ),
    SectionPrefix.SOLAR_CIRCUIT: (
        KebaKeEnergySwitchEntityDescription(
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
            key="priority_1_before_2",
            translation_key="priority_1_before_2",
        ),
    ),
    SectionPrefix.HEAT_PUMP: (
        KebaKeEnergySwitchEntityDescription(
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="compressor_use_night_speed",
            translation_key="compressor_use_night_speed",
        ),
    ),
    SectionPrefix.BUFFER_TANK: (
        KebaKeEnergySwitchEntityDescription(
            condition=has_photovoltaics,
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="use_excess_energy",
            translation_key="use_excess_energy",
        ),
    ),
    SectionPrefix.HOT_WATER_TANK: (
        KebaKeEnergySwitchEntityDescription(
            condition=has_photovoltaics,
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="use_excess_energy",
            translation_key="use_excess_energy",
        ),
    ),
    SectionPrefix.EXTERNAL_HEAT_SOURCE: (
        KebaKeEnergySwitchEntityDescription(
            condition=has_photovoltaics,
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            key="use_excess_energy",
            translation_key="use_excess_energy",
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: KebaKeEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEBA KeEnergy switches from a config entry."""
    async_setup_entities(
        entry,
        async_add_entities,
        SWITCH_TYPES,
        KebaKeEnergySwitchEntity,
        "switch",
    )
