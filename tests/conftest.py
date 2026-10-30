# Copyright 2025-2026 Michael Hacker
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

from custom_components.keba_keenergy.const import DOMAIN
from custom_components.keba_keenergy.const import PLATFORMS
from tests.api_data import CURVES_RESPONSE
from tests.api_data import DEVICE_INFO_RESPONSE
from tests.api_data import HMI_RESPONSE
from tests.api_data import MESSAGE_ID_SUFFIX
from tests.api_data import SYSTEM_RESPONSE
from tests.api_data import TIMEZONE_RESPONSE

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from collections.abc import Awaitable
    from collections.abc import Callable
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

    # The entity platforms log their errors (e.g. duplicate unique IDs) with the logger of the platform.
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
        self.responses: list[Exception | HTTPStatus | list[dict[str, Any]]] = []
        self.curves: HTTPStatus | list[list[dict[str, Any]]] = CURVES_RESPONSE
        self.system_name: str = SYSTEM_RESPONSE["name"]
        self.write_status: HTTPStatus = HTTPStatus.OK
        self.unsupported_variables: set[str] = set()
        self.message_ids: dict[str, int] = {}
        self.during_read: Callable[[], Awaitable[None]] | None = None
        self._values: dict[str, dict[str, Any]] = {}
        self._read_requests: list[str] = []

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

        The Web HMI keeps the values of the `responses`, a read of only the names of the next response takes it (the
        device counts, the options and the values of each update), the other reads (e.g. of `filter_supported()`)
        return the values it already has. An `HTTPStatus` returns an empty response with this status and an exception
        (e.g. `TimeoutError`) is raised by the next read.
        The message ids of the sensors come from `message_ids` (variable name to id, 0 if not given).
        The next read of the `responses` awaits `during_read` once before it responds, e.g. to set a value during an
        update.
        A read of an unknown value or of one of the `unsupported_variables` fails like the Web HMI rejects it. The
        values of the curves come from `curves` (an `HTTPStatus` fails them). The system name and the
        status of the write requests can be changed with `system_name` and `write_status`.
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

    async def _write_side_effect(self, method: str, url: URL, *_: object) -> AiohttpClientMockResponse:
        # A real request suspends, so other writes can queue for the write lock in the meantime.
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
        names: list[str] = [item["name"] for item in payload]
        response: Exception | HTTPStatus | list[dict[str, Any]]

        if all(".linTabPool[" in name for name in names):
            response = self._curve_response(payload)
        else:
            if self._takes_next_response(names):
                self._read_requests.append(str(data))
                next_response: Exception | HTTPStatus | list[dict[str, Any]] = self.responses.pop(0)

                if self.during_read:
                    during_read: Callable[[], Awaitable[None]] = self.during_read
                    self.during_read = None
                    await during_read()

                if not isinstance(next_response, list):
                    return self._error_response(method, url, next_response)

                self._values.update({value["name"]: value for value in next_response})

            # The values of the next responses are known as well, e.g. for the checks of `filter_supported()`.
            values: dict[str, dict[str, Any]] = {
                **{
                    value["name"]: value
                    for queued in reversed(self.responses)
                    if isinstance(queued, list)
                    for value in queued
                },
                **self._values,
            }
            unknown: list[str] = [
                name
                for name in names
                if name in self.unsupported_variables or (name not in values and not self._is_message_id(name))
            ]

            if unknown:
                # The Web HMI rejects the whole request and names the first unknown variable.
                return AiohttpClientMockResponse(
                    method,
                    url=url,
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                    text=f"Reading variable: {unknown[0]} failed",
                )

            # Like the Web HMI, only a read with `attr` "1" returns the attributes, e.g. the limits.
            response = [
                {"name": item["name"], "value": str(self.message_ids.get(item["name"], 0))}
                if self._is_message_id(item["name"])
                else values[item["name"]]
                if item["attr"] == "1"
                else {key: value for key, value in values[item["name"]].items() if key != "attributes"}
                for item in payload
            ]

        if not isinstance(response, list):
            return self._error_response(method, url, response)

        return AiohttpClientMockResponse(
            method,
            url=url,
            text=json.dumps(response),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )

    def _takes_next_response(self, names: list[str], /) -> bool:
        """Return True if a read takes the next of the `responses`.

        An error is taken by the next read, values by the next read of only their names (and message ids), e.g. not
        by the checks of `filter_supported()`, which read the values of several responses at once.
        """
        if not self.responses:
            return False

        next_response: Exception | HTTPStatus | list[dict[str, Any]] = self.responses[0]

        if not isinstance(next_response, list):
            return True

        response_names: set[str] = {value["name"] for value in next_response}
        return all(
            name in response_names or name in self.unsupported_variables or self._is_message_id(name) for name in names
        )

    @staticmethod
    def _is_message_id(name: str, /) -> bool:
        return name.endswith(MESSAGE_ID_SUFFIX)

    @staticmethod
    def _error_response(method: str, url: URL, error: Exception | HTTPStatus, /) -> AiohttpClientMockResponse:
        """Return an empty response with the status, or raise the exception."""
        if isinstance(error, Exception):
            raise error

        return AiohttpClientMockResponse(method, url=url, status=error)

    def _curve_response(self, payload: list[dict[str, str]], /) -> HTTPStatus | list[dict[str, Any]]:
        """Return the requested values of the curves.

        `get_curve_tables()` reads the names alone, then the points with the name of their curve,
        so `curves` holds the names and the points separately, like the Web HMI may return different names.
        """
        if isinstance(self.curves, HTTPStatus):
            return self.curves

        names, points = self.curves
        is_names_request: bool = all(item["name"].endswith(".name") for item in payload)
        values: dict[str, dict[str, Any]] = {value["name"]: value for value in (names if is_names_request else points)}
        return [values[item["name"]] for item in payload]

    async def setup_integration(self) -> None:
        """Register all requests for the host of the config entry and set up the integration."""
        self.register_requests(self.config_entry.data[CONF_HOST], ssl=self.config_entry.data[CONF_SSL])
        self.config_entry.add_to_hass(self.hass)

        assert await self.hass.config_entries.async_setup(self.config_entry.entry_id)
        await self.hass.async_block_till_done()

    def read_requests(self) -> list[str]:
        """Return the bodies of the read requests that took one of the `responses`, in order."""
        return list(self._read_requests)

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
