from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import UpdateFailed
from keba_keenergy_api.error import APIError

from custom_components.keba_keenergy.coordinator import KebaKeEnergyDataUpdateCoordinator

if TYPE_CHECKING:
    from aiohttp import ClientSession


async def test_async_update_data_api_error_raises_update_failed(
    hass: HomeAssistant,
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
            new=AsyncMock(side_effect=APIError("boom")),
        ),
        pytest.raises(UpdateFailed) as error,
    ):
        await coordinator._async_update_data()

    assert str(error.value) == "boom"
