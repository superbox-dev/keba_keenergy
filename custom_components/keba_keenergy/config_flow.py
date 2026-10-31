# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0
"""Config flow for KEBA KeEnergy."""

from __future__ import annotations

import logging
import math
from http import HTTPStatus
from ipaddress import IPv4Address
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

import probatio
from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntryState
from homeassistant.config_entries import ConfigFlow
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.config_entries import OptionsFlowWithReload
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.const import CONF_SSL
from homeassistant.const import CONF_USERNAME
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import NumberSelector
from homeassistant.helpers.selector import NumberSelectorConfig
from homeassistant.helpers.selector import NumberSelectorMode
from homeassistant.util.network import is_ip_address
from keba_keenergy_api.client import KebaKeEnergyAPI
from keba_keenergy_api.exceptions import APIError

from .const import CONFIG_ENTRY_VERSION
from .const import DEFAULT_SCAN_INTERVAL
from .const import DOMAIN
from .const import MANUFACTURER
from .const import MIN_SCAN_INTERVAL
from .const import NAME
from .const import SCAN_INTERVAL_TICK_OPTIONS
from .const import STEP_AUTH_DATA_SCHEMA

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aiohttp import ClientSession
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
    from keba_keenergy_api.models import DeviceInfo

    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator


_LOGGER: Final = logging.getLogger(__name__)


class KebaKeEnergyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for KEBA KeEnergy."""

    VERSION: int = CONFIG_ENTRY_VERSION

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.host: str = ""
        self.ssl: bool = False
        self.serial_number: str | None = None

        self._entry: KebaKeEnergyConfigEntry | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.host = user_input[CONF_HOST]
            requires_authentication: bool = await self._async_check_authentication_required()

            if requires_authentication:
                return await self.async_step_auth(user_input)

            errors = await self._async_validate_or_error(user_input)

            if self.serial_number and not errors:
                return await self._async_complete_entry(user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=probatio.Schema(
                {
                    probatio.Required(CONF_HOST, default=self.host): str,
                    probatio.Required(CONF_SSL, default=self.ssl): bool,
                },
            ),
            errors=errors,
            description_placeholders={
                "name": f"{MANUFACTURER} {NAME}",
                "host": self.host,
            },
        )

    async def _async_check_authentication_required(self) -> bool:
        """Return True if the Web HMI requires authentication, which also enables SSL."""
        session: ClientSession = async_get_clientsession(self.hass)
        requires_authentication: bool = False

        try:
            async with session.get(f"https://{self.host}", ssl=False) as response:
                if response.status == HTTPStatus.UNAUTHORIZED:
                    self.ssl = True
                    requires_authentication = True
        except ClientError as error:
            _LOGGER.debug("Cannot check the authentication of %s: %s", self.host, error)

        return requires_authentication

    async def _async_validate_or_error(self, user_input: dict[str, Any]) -> dict[str, str]:
        """Read the serial number with the user input, return the errors of the form if that fails."""
        errors: dict[str, str] = {}

        try:
            self.serial_number = await self._async_get_serial_number(user_input)
        except CannotConnectError:
            errors["base"] = "cannot_connect"
        except InvalidAuthError:
            errors["base"] = "invalid_auth"
        except Exception:
            errors["base"] = "unknown"
            _LOGGER.exception("Unexpected exception")

        return errors

    async def _async_get_serial_number(self, data: dict[str, Any], /) -> str:
        """Connect to the Web HMI with the user input and return its serial number."""
        session: ClientSession = async_get_clientsession(self.hass)
        _LOGGER.debug("Try to connect to %s", data[CONF_HOST])

        client: KebaKeEnergyAPI = KebaKeEnergyAPI(
            data[CONF_HOST],
            session=session,
            username=data.get(CONF_USERNAME),
            password=data.get(CONF_PASSWORD),
            ssl=data[CONF_SSL],
            verify_ssl=False,
        )

        try:
            response: DeviceInfo = await client.get_device_info()
        except APIError as error:
            _LOGGER.debug("API error %s", error)
            if error.status == HTTPStatus.UNAUTHORIZED:
                raise InvalidAuthError from error

            raise CannotConnectError from error
        else:
            _LOGGER.debug("Connected to %s", data[CONF_HOST])

        return str(response["serNo"])

    async def _async_complete_entry(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        await self.async_set_unique_id(self.serial_number)

        if self._entry is not None:
            self._abort_if_unique_id_mismatch(
                reason="wrong_account",
                description_placeholders={
                    "name": f"{MANUFACTURER} {NAME}",
                },
            )

            return self.async_update_reload_and_abort(
                self._entry,
                data_updates=user_input,
            )

        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=f"{MANUFACTURER} {NAME} ({self.host})", data=user_input)

    async def async_step_auth(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Authenticate to the device."""
        errors: dict[str, str] = {}

        if user_input is not None and user_input.get(CONF_USERNAME) and user_input.get(CONF_PASSWORD):
            user_input[CONF_HOST] = self.host
            user_input[CONF_SSL] = self.ssl

            errors = await self._async_validate_or_error(user_input)

            if self.serial_number and not errors:
                return await self._async_complete_entry(user_input)

        return self.async_show_form(
            step_id="auth",
            data_schema=STEP_AUTH_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "name": f"{MANUFACTURER} {NAME}",
            },
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        """Perform reauth after an authentication error."""
        self.host = entry_data[CONF_HOST]
        self.ssl = entry_data[CONF_SSL]

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle reauth confirmation flow."""
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_HOST] = self.host
            user_input[CONF_SSL] = self.ssl

            errors = await self._async_validate_or_error(user_input)

            if self.serial_number and not errors:
                self._entry = self._get_reauth_entry()
                return await self._async_complete_entry(user_input)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_AUTH_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "name": f"{MANUFACTURER} {NAME}",
            },
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        _LOGGER.debug("Discovered %s", discovery_info.hostname)

        self.host = discovery_info.hostname[0:-1]
        self.serial_number = discovery_info.properties["serialnumber"]

        await self.async_set_unique_id(self.serial_number)
        self._abort_if_unique_id_configured(updates=self._discovery_updates(discovery_info))

        return await self.async_step_discovery_confirm()

    def _discovery_updates(self, discovery_info: ZeroconfServiceInfo, /) -> dict[str, str] | None:
        """Return the new IP address of a configured device, a configured host name is kept."""
        entry: KebaKeEnergyConfigEntry | None = self.hass.config_entries.async_entry_for_domain_unique_id(
            DOMAIN,
            self.serial_number or "",
        )

        if (
            entry is None
            or not isinstance(discovery_info.ip_address, IPv4Address)
            or not is_ip_address(entry.data[CONF_HOST])
        ):
            return None

        return {CONF_HOST: str(discovery_info.ip_address)}

    async def async_step_discovery_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle user-confirmation of discovered node."""
        errors: dict[str, str] = {}
        requires_authentication: bool = await self._async_check_authentication_required()

        if requires_authentication:
            return await self.async_step_auth(user_input)

        if user_input is not None:
            user_input[CONF_HOST] = self.host
            user_input[CONF_SSL] = self.ssl

            errors = await self._async_validate_or_error(user_input)

            if self.serial_number and not errors:
                return await self._async_complete_entry(user_input)

        return self.async_show_form(
            step_id="discovery_confirm",
            data_schema=None,
            errors=errors,
            description_placeholders={
                "name": f"{MANUFACTURER} {NAME}",
                "host": self.host,
            },
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        self._entry = self._get_reconfigure_entry()

        self.host = self._entry.data[CONF_HOST]
        self.ssl = self._entry.data[CONF_SSL]

        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: KebaKeEnergyConfigEntry,  # noqa: ARG004
    ) -> KebaKeEnergyOptionsFlow:
        """Get the options flow for this handler."""
        return KebaKeEnergyOptionsFlow()


class KebaKeEnergyOptionsFlow(OptionsFlowWithReload):
    """Options flow for KEBA KeEnergy."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the options of the scan interval and the multipliers of the installed device types."""
        if user_input is not None:
            return self.async_create_entry(data=self._normalize_user_input(user_input))

        if self.config_entry.state is not ConfigEntryState.LOADED:
            return self.async_abort(reason="options_not_ready")

        coordinator: KebaKeEnergyDataUpdateCoordinator = self.config_entry.runtime_data

        schema_fields: dict[probatio.Required, object] = {}

        schema_fields[
            probatio.Required(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            )
        ] = NumberSelector(
            NumberSelectorConfig(
                min=MIN_SCAN_INTERVAL,
                step=1,
                mode=NumberSelectorMode.BOX,
            ),
        )

        # The control unit is always installed, so the system multiplier is always shown.
        for device_type, conf_key in SCAN_INTERVAL_TICK_OPTIONS.items():
            if coordinator.has_device(device_type):
                schema_fields[
                    probatio.Required(
                        conf_key,
                        default=self.config_entry.options.get(conf_key, 1),
                    )
                ] = NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=180,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    ),
                )

        return self.async_show_form(
            step_id="init",
            data_schema=probatio.Schema(schema_fields),
        )

    @staticmethod
    def _normalize_user_input(user_input: dict[str, Any], /) -> dict[str, Any]:
        """Return the user input with the greatest common divisor of the multipliers moved into the scan interval.

        E.g. a scan interval of 20 s with the multipliers 2 and 4 becomes 40 s with the multipliers 1 and 2. The number
        selectors return floats, the options are stored as integers.
        """
        scan_interval: int = int(user_input[CONF_SCAN_INTERVAL])
        ticks: dict[str, int] = {
            key: int(user_input[key]) for key in SCAN_INTERVAL_TICK_OPTIONS.values() if key in user_input
        }
        # The system multiplier is always in the user input, so the divisor is at least 1.
        gcd: int = math.gcd(*ticks.values())

        user_input[CONF_SCAN_INTERVAL] = scan_interval * gcd
        user_input.update({key: tick // gcd for key, tick in ticks.items()})

        _LOGGER.debug("Tick normalization: %s -> gcd=%s", user_input, gcd)

        return user_input


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuthError(HomeAssistantError):
    """Error to indicate there is invalid auth."""
