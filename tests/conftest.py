import json
from typing import Any

import pytest
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMockResponse
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from syrupy.assertion import SnapshotAssertion
from yarl import URL

from tests.api_data import data_response
from tests.api_data import device_info_response
from tests.api_data import positions_response
from tests.api_data import system_response


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
        self._responses: list[list[dict[str, Any]]] = [positions_response, data_response]

    def register_requests(self) -> None:
        self._aioclient_mock.post(
            "http://ap4400.local/deviceControl?action=getDeviceInfo",
            text=json.dumps(device_info_response),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self._aioclient_mock.post(
            "http://ap4400.local/swupdate?action=getSystemInstalled",
            text=json.dumps(system_response),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self._aioclient_mock.post(
            "http://ap4400.local/var/readWriteVars",
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
