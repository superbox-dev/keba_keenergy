from typing import Any
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import UpdateFailed
from keba_keenergy_api.error import APIError
from keba_keenergy_api.error import AuthenticationError

from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.coordinator import KebaKeEnergyDataUpdateCoordinator

if TYPE_CHECKING:
    from aiohttp import ClientSession


@pytest.mark.parametrize(
    ("side_effect", "raise_exception", "expected_translation_key", "expected_error"),
    [
        (APIError("boom"), UpdateFailed, "communication_error", {"error": "boom"}),
        (AuthenticationError("boom"), ConfigEntryAuthFailed, "authentication_error", None),
    ],
)
async def test_async_update_data_api_error_raises_update_failed(
    hass: HomeAssistant,
    side_effect: Exception,
    raise_exception: type[HomeAssistantError],
    expected_translation_key: str,
    expected_error: dict[str, Any] | None,
) -> None:
    session: ClientSession = async_get_clientsession(hass, verify_ssl=False)

    coordinator: KebaKeEnergyDataUpdateCoordinator = KebaKeEnergyDataUpdateCoordinator(
        hass,
        host="10.0.0.100",
        username=None,
        password=None,
        ssl=False,
        session=session,
    )

    with (
        patch.object(
            coordinator.api,
            "read_data",
            new=AsyncMock(side_effect=side_effect),
        ),
        pytest.raises(raise_exception) as error,
    ):
        await coordinator._async_update_data()

    assert error.value.translation_domain == DOMAIN
    assert error.value.translation_key == expected_translation_key
    assert error.value.translation_placeholders == expected_error
