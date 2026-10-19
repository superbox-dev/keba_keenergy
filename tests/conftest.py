# Copyright 2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Fixtures for the KEBA KeEnergy tests."""

from __future__ import annotations

import asyncio
import json
import logging
from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_SSL
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMockResponse
from yarl import URL

from custom_components.keba_keenergy import PLATFORMS
from custom_components.keba_keenergy.const import DOMAIN
from tests import setup_integration
from tests.api_data import DEVICE_INFO_RESPONSE
from tests.api_data import HEATING_CURVES_RESPONSE
from tests.api_data import HMI_RESPONSE
from tests.api_data import SYSTEM_RESPONSE
from tests.api_data import TIMEZONE_RESPONSE

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from collections.abc import Generator

    from _pytest.fixtures import SubRequest
    from homeassistant.core import HomeAssistant
    from syrupy.assertion import SnapshotAssertion


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Home Assistant extension."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable the custom integrations in Home Assistant."""


@pytest.fixture(autouse=True)
async def fail_on_log_errors(
    hass: HomeAssistant,
    request: pytest.FixtureRequest,
) -> AsyncGenerator[None]:
    """Fail test on Home Assistant or integration errors."""
    if request.node.get_closest_marker("no_fail_on_keba_errors"):
        yield
        return

    records: list[logging.LogRecord] = []

    class ErrorHandler(logging.Handler):
        """Capture error log records."""

        def emit(self, record: logging.LogRecord) -> None:
            """Capture the record if it is an error."""
            if record.levelno >= logging.ERROR:
                records.append(record)

    handler: ErrorHandler = ErrorHandler()

    # The entity platforms log their errors (e.g. duplicate unique IDs) with the logger of the platform
    loggers: list[logging.Logger] = [
        logging.getLogger("custom_components.keba_keenergy"),
        logging.getLogger("homeassistant.helpers.entity_platform"),
        *(logging.getLogger(f"homeassistant.components.{platform}") for platform in PLATFORMS),
    ]

    for logger in loggers:
        logger.addHandler(handler)

    try:
        yield
        await hass.async_block_till_done()

    finally:
        for logger in loggers:
            logger.removeHandler(handler)

    if records:
        msgs: str = "\n".join(record.getMessage() for record in records)
        pytest.fail(f"Keba integration logged errors:\n{msgs}")


class FakeKebaKeEnergyAPI:
    """Fake Web HMI of a KEBA KeEnergy control unit, based on the mocked HTTP requests."""

    def __init__(
        self,
        hass: HomeAssistant,
        aioclient_mock: AiohttpClientMocker,
        config_entry: MockConfigEntry,
    ) -> None:
        """Initialize the fake Web HMI.

        Parameters
        ----------
        hass
            The Home Assistant instance of the test.
        aioclient_mock
            The mocker of the HTTP requests.
        config_entry
            The config entry that is set up by `setup_integration()`.

        """
        self.hass: HomeAssistant = hass
        self.aioclient_mock: AiohttpClientMocker = aioclient_mock
        self.config_entry: MockConfigEntry = config_entry
        self.responses: list[list[dict[str, Any]] | HTTPStatus | Exception] = []
        self.heating_curves: list[list[dict[str, Any]]] | HTTPStatus = HEATING_CURVES_RESPONSE
        self.system_name: str = SYSTEM_RESPONSE["name"]
        self.write_status: HTTPStatus = HTTPStatus.OK
        self.unsupported_variables: set[str] = set()

    def register_auth_request(self, host: str, /, *, status: int = 200, exc: Exception | None = None) -> None:
        """Register the request that checks if the Web HMI requires authentication."""
        self.aioclient_mock.get(f"https://{host}", status=status, exc=exc)

    def register_get_device_info(
        self,
        host: str,
        /,
        *,
        ssl: bool = False,
        status: int = 200,
        exc: Exception | None = None,
    ) -> None:
        """Register the request of the device info."""
        schema: str = "https" if ssl else "http"

        self.aioclient_mock.post(
            f"{schema}://{host}/deviceControl?action=getDeviceInfo",
            text=json.dumps(DEVICE_INFO_RESPONSE),
            headers={"Content-Type": "application/json;charset=utf-8"},
            status=status,
            exc=exc,
        )

    def register_requests(self, host: str, /, *, ssl: bool = False) -> None:
        """Register all requests of the setup and the updates.

        The read requests return the `responses` in order, an `HTTPStatus` returns an empty response with this status
        and an exception (e.g. `TimeoutError`) is raised by the request.
        The requests of `filter_request()` succeed, except for the `unsupported_variables`, which the Web HMI does not
        know and which are also left out of the responses. The values of the heating curves come from `heating_curves`
        (an `HTTPStatus` fails them). The system name and the status of the write requests can be changed with
        `system_name` and `write_status`.
        """
        schema: str = "https" if ssl else "http"

        self.register_get_device_info(host, ssl=ssl)

        self.aioclient_mock.post(
            f"{schema}://{host}/swupdate?action=getSystemInstalled",
            text=json.dumps({**SYSTEM_RESPONSE, "name": self.system_name}),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self.aioclient_mock.post(
            f"{schema}://{host}/swupdate?action=getHmiInstalled",
            text=json.dumps(HMI_RESPONSE),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self.aioclient_mock.post(
            f"{schema}://{host}/dateTime?action=getTimeZone",
            text=json.dumps(TIMEZONE_RESPONSE),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

        self.aioclient_mock.post(
            f"{schema}://{host}/var/readWriteVars",
            params={"action": "set"},
            side_effect=self._write_side_effect,
        )

        self.aioclient_mock.post(
            f"{schema}://{host}/var/readWriteVars",
            side_effect=self._read_side_effect,
        )

    async def setup_integration(self) -> None:
        """Register all requests for the host of the config entry and set up the integration."""
        self.register_requests(self.config_entry.data[CONF_HOST], ssl=self.config_entry.data[CONF_SSL])
        await setup_integration(self.hass, self.config_entry)

    @staticmethod
    def is_filter_request(data: object, /) -> bool:
        """Return True for a request of `filter_request()`, which reads all values without attributes.

        The values of the heating curves are also read without attributes, but never by `filter_request()`.
        """
        payload: list[dict[str, str]] = json.loads(str(data))
        return all(item["attr"] == "0" and ".linTabPool[" not in item["name"] for item in payload)

    def _heating_curve_response(self, payload: list[dict[str, str]], /) -> list[dict[str, Any]] | HTTPStatus:
        """Return the requested values of the heating curves.

        The names are read alone (`get_available_heating_curves()`), the points with the name of their heating curve,
        so `heating_curves` holds the names and the points separately, like the Web HMI may return different names.
        """
        if isinstance(self.heating_curves, HTTPStatus):
            return self.heating_curves

        names, points = self.heating_curves
        is_names_request: bool = all(item["name"].endswith(".name") for item in payload)
        values: dict[str, dict[str, Any]] = {value["name"]: value for value in (names if is_names_request else points)}
        return [values[item["name"]] for item in payload]

    async def _write_side_effect(self, method: str, url: URL, *_: object) -> AiohttpClientMockResponse:
        # A real request suspends, so other writes can queue for the write lock in the meantime
        await asyncio.sleep(0)

        return AiohttpClientMockResponse(
            method,
            url=url,
            text="[{}]",
            status=self.write_status,
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

    async def _read_side_effect(self, method: str, url: URL, data: object, *_: object) -> AiohttpClientMockResponse:
        payload: list[dict[str, str]] = json.loads(str(data))
        response: list[dict[str, Any]] | HTTPStatus | Exception

        if self.is_filter_request(data):
            unknown: list[str] = [item["name"] for item in payload if item["name"] in self.unsupported_variables]

            if unknown:
                # The Web HMI rejects the whole request and names the first unknown variable
                return AiohttpClientMockResponse(
                    method,
                    url=url,
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                    text=f"Reading variable: {unknown[0]} failed",
                )

            response = []
        elif all(".linTabPool[" in item["name"] for item in payload):
            response = self._heating_curve_response(payload)
        elif not self.responses:
            return AiohttpClientMockResponse(method, url=url)
        else:
            response = self.responses.pop(0)

            if isinstance(response, list):
                response = [value for value in response if value["name"] not in self.unsupported_variables]

        if isinstance(response, Exception):
            raise response

        if isinstance(response, HTTPStatus):
            return AiohttpClientMockResponse(method, url=url, status=response)

        return AiohttpClientMockResponse(
            method,
            url=url,
            text=json.dumps(response),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

    def read_requests(self) -> list[str]:
        """Return the bodies of all read requests, in order."""
        return [
            str(data)
            for method, url, data, _ in self.aioclient_mock.mock_calls
            if method == "POST"
            and url.path == "/var/readWriteVars"
            and "action" not in url.query
            and not self.is_filter_request(data)
        ]

    def assert_called_write_with(self, data: str, /) -> None:
        """Assert that the data was written to the Web HMI."""
        assert data in self.write_requests()

    def write_requests(self) -> list[str]:
        """Return the bodies of all write requests, in order."""
        return [
            str(data)
            for method, url, data, _ in self.aioclient_mock.mock_calls
            if method == "POST" and url == URL("http://10.0.0.100/var/readWriteVars?action=set")
        ]


@pytest.fixture
async def fake_api(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    config_entry: MockConfigEntry,
) -> FakeKebaKeEnergyAPI:
    """Return the fake Web HMI."""
    return FakeKebaKeEnergyAPI(hass, aioclient_mock, config_entry)


@pytest.fixture
def language(hass: HomeAssistant, request: SubRequest) -> str:
    """Set the language of Home Assistant, parametrized indirectly."""
    hass.config.language = request.param
    return request.param


@pytest.fixture
def config_entry(request: SubRequest) -> MockConfigEntry:
    """Return the config entry, parametrized indirectly with `data` and `options` to update."""
    mock_config_entry_data: dict[str, Any] = {
        "title": "KEBA KeEnergy (ap4400.local)",
        "data": {
            CONF_HOST: "10.0.0.100",
            CONF_SSL: False,
        },
        "unique_id": "12345678",
        "options": {
            "scan_interval": 20,
            "scan_interval_tick_system": 1,
            "scan_interval_tick_heat_pump": 1,
            "scan_interval_tick_heat_circuit": 1,
            "scan_interval_tick_solar_circuit": 1,
            "scan_interval_tick_hot_water_tank": 1,
            "scan_interval_tick_buffer_tank": 1,
            "scan_interval_tick_switch_valve": 1,
            "scan_interval_tick_passive_cooling": 1,
            "scan_interval_tick_external_heat_source": 1,
            "scan_interval_tick_photovoltaics": 1,
        },
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
