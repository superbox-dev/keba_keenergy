from homeassistant.core import HomeAssistant
from homeassistant.helpers.translation import async_get_translations
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def setup_integration(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    """Set up the KEBA KeEnergy integration in Home Assistant."""
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


async def init_translations(hass: HomeAssistant, config_entry: MockConfigEntry, /, *, category: str) -> dict[str, str]:
    """Set up the KEBA KeEnergy integration in Home Assistant."""
    translations: dict[str, str] = await async_get_translations(
        hass,
        hass.config.language,
        category,
        [config_entry.domain],
    )

    return translations
