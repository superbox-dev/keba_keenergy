from unittest.mock import patch

from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.translation import async_get_translations
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.keba_keenergy.const import DOMAIN
from tests import setup_integration
from tests.api_data import MULTIPLE_POSITIONS_RESPONSE
from tests.api_data import MULTIPLE_POSITION_DATA_RESPONSE_1
from tests.api_data import get_multiple_position_fixed_data_response
from tests.conftest import FakeKebaKeEnergyAPI


async def test_set_value(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    fake_api: FakeKebaKeEnergyAPI,
) -> None:
    fake_api.responses = [
        MULTIPLE_POSITIONS_RESPONSE,
        get_multiple_position_fixed_data_response(),
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        # Read API after services call
        MULTIPLE_POSITION_DATA_RESPONSE_1,
        MULTIPLE_POSITION_DATA_RESPONSE_1,
    ]
    fake_api.register_requests("10.0.0.100")

    with patch(
        "homeassistant.helpers.storage.Store.async_load",
        return_value={
            "flash_write_counter": {
                "week": [2026, 5],
                "count": 1,
            },
        },
    ):
        await setup_integration(hass, config_entry)

    with patch("custom_components.keba_keenergy.coordinator.FLASH_WRITE_LIMIT_PER_WEEK", 1):
        await hass.services.async_call(
            domain=SELECT_DOMAIN,
            service=SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: "select.keba_keenergy_12345678_buffer_tank_operating_mode_1",
                ATTR_OPTION: "off",
            },
            blocking=True,
        )

        await hass.services.async_call(
            domain=SELECT_DOMAIN,
            service=SERVICE_SELECT_OPTION,
            service_data={
                ATTR_ENTITY_ID: "select.keba_keenergy_12345678_buffer_tank_operating_mode_1",
                ATTR_OPTION: "on",
            },
            blocking=True,
        )
    issue_registry = ir.async_get(hass)

    issue = issue_registry.async_get_issue(
        DOMAIN,
        "frequent_flash_writes",
    )

    assert issue is not None
    assert issue.severity == ir.IssueSeverity.WARNING

    translations_en = await async_get_translations(
        hass,
        "en",
        "issues",
        {DOMAIN},
    )

    title_en: str = translations_en[f"component.{DOMAIN}.issues.{issue.translation_key}.title"]
    description_en: str = translations_en[f"component.{DOMAIN}.issues.{issue.translation_key}.description"].format(
        **(issue.translation_placeholders or {}),
    )

    assert title_en == "Frequent write operations detected"
    assert description_en == (
        """More than 1 write operations were performed on the device this week.

Very frequent write operations (for example caused by automations) may reduce the lifetime of the device's flash memory."""  # noqa: E501
    )

    translations_de = await async_get_translations(
        hass,
        "de",
        "issues",
        {DOMAIN},
    )

    title_de: str = translations_de[f"component.{DOMAIN}.issues.{issue.translation_key}.title"]
    description_de: str = translations_de[f"component.{DOMAIN}.issues.{issue.translation_key}.description"].format(
        **(issue.translation_placeholders or {}),
    )

    assert title_de == "Viele Schreibzugriffe erkannt"
    assert description_de == (
        """In dieser Woche wurden mehr als 1 Schreibzugriffe auf das Gerät durchgeführt.

Sehr häufige Schreibzugriffe (zum Beispiel durch Automationen) können die Lebensdauer des Flash-Speichers des Geräts reduzieren."""  # noqa: E501
    )
