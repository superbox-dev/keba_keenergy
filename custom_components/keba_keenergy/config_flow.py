"""Config flow for KEBA KeEnergy."""

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from aiohttp import ClientError
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_SSL
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from keba_keenergy_api.api import KebaKeEnergyAPI
from keba_keenergy_api.error import APIError

from .const import CONFIG_ENTRY_VERSION
from .const import DEFAULT_SSL
from .const import DOMAIN
from .const import MANUFACTURER
from .const import NAME

CONFIG_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
    },
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, /, *, host: str, ssl: bool) -> str:
    """Validate the user input allows us to connect."""
    session: aiohttp.ClientSession = async_get_clientsession(hass)
    _LOGGER.debug("Connecting to %s", host)

    client: KebaKeEnergyAPI = KebaKeEnergyAPI(host, session=session, ssl=ssl)

    try:
        response: dict[str, Any] = await client.system.get_device_info()
    except (APIError, ClientError) as error:
        raise CannotConnectError from error

    return str(response["serNo"])


class KebaKeEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for KEBA KeEnergy."""

    VERSION: int = CONFIG_ENTRY_VERSION

    def __init__(self) -> None:
        """Initialize flow."""
        self._host: str = ""
        self._ssl: bool = False
        self._serial_number: str | None = None

    @callback
    def _async_get_entry(self) -> ConfigFlowResult:
        return self.async_create_entry(
            title=f"{MANUFACTURER} {NAME} ({self._host})",
            data={
                CONF_HOST: self._host,
                CONF_SSL: self._ssl,
            },
        )

    async def _set_uid_and_abort(self) -> None:
        await self.async_set_unique_id(self._serial_number)
        self._abort_if_unique_id_configured(
            updates={
                CONF_HOST: self._host,
                CONF_SSL: self._ssl,
            },
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._ssl = user_input[CONF_SSL]

            try:
                self._serial_number = await validate_input(self.hass, host=self._host, ssl=self._ssl)
            except CannotConnectError:
                _LOGGER.debug("Can't connect to KEBA KeEnergy API", exc_info=True)
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.debug("Unknown error trying to connect")
                errors["base"] = "unknown"

            if self._serial_number:
                await self._set_uid_and_abort()
                return self._async_get_entry()

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
            description_placeholders={
                "name": f"{MANUFACTURER} {NAME}",
                "host": self._host,
            },
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        _LOGGER.debug("Starting discovery via: %s", discovery_info)

        self._host = discovery_info.hostname[0:-1]
        self._ssl = False
        self._serial_number = discovery_info.properties["serialnumber"]

        await self._set_uid_and_abort()
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle user-confirmation of discovered node."""
        if user_input is not None:
            try:
                await validate_input(self.hass, host=self._host, ssl=self._ssl)
                return self._async_get_entry()
            except CannotConnectError:
                _LOGGER.debug("Can't connect to KEBA KeEnergy API", exc_info=True)
                return self.async_abort(reason="cannot_connect")

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={
                "name": f"{MANUFACTURER} {NAME}",
                "host": self._host,
            },
        )


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""
