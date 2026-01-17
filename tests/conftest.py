import json
from collections.abc import Generator
from typing import Any
from unittest.mock import patch

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
from tests.api_data import DEVICE_INFO_RESPONSE
from tests.api_data import FILTER_REQUESTS
from tests.api_data import HMI_RESPONSE
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
        self.aioclient_mock: AiohttpClientMocker = aioclient_mock
        self._responses: list[list[dict[str, Any]]] = []

    @property
    def responses(self) -> list[list[dict[str, Any]]]:
        return self._responses

    @responses.setter
    def responses(self, value: list[list[dict[str, Any]]]) -> None:
        self._responses = value

    def register_auth_request(self, host: str, /, *, status: int = 200, exc: Exception | None = None) -> None:
        self.aioclient_mock.get(f"https://{host}", status=status, exc=exc)

    def register_requests(self, host: str, /, *, ssl: bool = False) -> None:
        schema: str = "https" if ssl else "http"

        self.aioclient_mock.post(
            f"{schema}://{host}/deviceControl?action=getDeviceInfo",
            text=json.dumps(DEVICE_INFO_RESPONSE),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self.aioclient_mock.post(
            f"{schema}://{host}/swupdate?action=getSystemInstalled",
            text=json.dumps(SYSTEM_RESPONSE),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self.aioclient_mock.post(
            f"{schema}://{host}/swupdate?action=getHmiInstalled",
            text=json.dumps(HMI_RESPONSE),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self.aioclient_mock.post(
            f"{schema}://{host}/var/readVarChildren",
            text=json.dumps(FILTER_REQUESTS),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self.aioclient_mock.post(
            f"{schema}://{host}/var/readWriteVars",
            text="[{}]",
            params={"action": "set"},
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self.aioclient_mock.post(
            f"{schema}://{host}/var/readWriteVars",
            side_effect=self._add_sideeffect,
        )

    async def _add_sideeffect(self, method: str, url: URL, *args: Any) -> AiohttpClientMockResponse:  # noqa: ARG002
        if len(self._responses) > 0:
            response = self._responses.pop(0)

            return AiohttpClientMockResponse(
                method,
                url=url,
                text=json.dumps(response),
                headers={"Content-Type": "application/json;charset=utf-8"},
            )

        return AiohttpClientMockResponse(method, url=url)

    def assert_called_write_with(self, data: str, /) -> None:
        assert (
            "POST",
            URL("http://10.0.0.100/var/readWriteVars?action=set"),
            data,
            None,
        ) in self.aioclient_mock.mock_calls


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


@pytest.fixture
def entity_registry_enabled_by_default() -> Generator[None]:
    """Test fixture that ensures all entities are enabled in the registry."""
    with (
        patch(
            "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
            return_value=True,
        ),
    ):
        yield
