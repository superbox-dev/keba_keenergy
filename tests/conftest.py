import json
from typing import Any

import pytest
from _pytest.fixtures import SubRequest
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_SSL
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMockResponse
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from syrupy.assertion import SnapshotAssertion
from yarl import URL

from custom_components.keba_keenergy.const import DOMAIN
from tests.api_data import DATA_RESPONSE
from tests.api_data import DEVICE_INFO_RESPONSE
from tests.api_data import POSITIONS_RESPONSE
from tests.api_data import SYSTEM_RESPONSE


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Home Assistant extension."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:  # noqa: ARG001
    return


class FakeKebaKeEnergyAPI:
    def __init__(self, aioclient_mock: AiohttpClientMocker) -> None:
        self._aioclient_mock: AiohttpClientMocker = aioclient_mock
        self._responses: list[list[dict[str, Any]]] = [POSITIONS_RESPONSE, DATA_RESPONSE]

    def register_requests(self, host: str, /) -> None:
        self._aioclient_mock.post(
            f"http://{host}/deviceControl?action=getDeviceInfo",
            text=json.dumps(DEVICE_INFO_RESPONSE),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self._aioclient_mock.post(
            f"http://{host}/swupdate?action=getSystemInstalled",
            text=json.dumps(SYSTEM_RESPONSE),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self._aioclient_mock.post(
            f"http://{host}/var/readWriteVars",
            side_effect=self.request,
        )

    async def request(self, method: str, url: URL, *args: Any) -> AiohttpClientMockResponse:  # noqa: ARG002
        response = self._responses.pop(0)

        return AiohttpClientMockResponse(
            method,
            url,
            text=json.dumps(response),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )


@pytest.fixture
async def fake_api(
    aioclient_mock: AiohttpClientMocker,
) -> FakeKebaKeEnergyAPI:
    return FakeKebaKeEnergyAPI(aioclient_mock)


@pytest.fixture
def config_entry(request: SubRequest) -> MockConfigEntry:
    mock_config_entry_data: dict[str, Any] = {
        "title": "KEBA KeEnergy (ap4400.local)",
        "data": {
            CONF_HOST: "10.0.0.100",
            CONF_SSL: False,
        },
        "unique_id": "12345678",
    }

    if hasattr(request, "param"):
        mock_config_entry_data.update(request.param)

    return MockConfigEntry(
        domain=DOMAIN,
        **mock_config_entry_data,
    )
