"""Config flow for KEBA KeEnergy."""

import logging
from http import HTTPStatus
from typing import Any
from typing import TYPE_CHECKING

import voluptuous as vol
from aiohttp import ClientError
from homeassistant.config_entries import ConfigFlow
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_SSL
from homeassistant.const import CONF_USERNAME
from homeassistant.core import HomeAssistant
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

if TYPE_CHECKING:
    from aiohttp import ClientSession

STEP_USER_DATA_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
    },
)

STEP_AUTH_DATA_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    },
)


_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, /, *, data: dict[str, Any]) -> str:
    """Validate the user input allows us to connect."""
    session: ClientSession = async_get_clientsession(hass)
    _LOGGER.debug("Try to connected to %s", data[CONF_HOST])

    client: KebaKeEnergyAPI = KebaKeEnergyAPI(
        data[CONF_HOST],
        session=session,
        username=data.get(CONF_USERNAME),
        password=data.get(CONF_PASSWORD),
        ssl=data[CONF_SSL],
        skip_ssl_verification=True,
    )

    try:
        response: dict[str, Any] = await client.system.get_device_info()
    except APIError as error:
        _LOGGER.debug("API error %s", error)
        if error.status == HTTPStatus.UNAUTHORIZED:
            raise InvalidAuthError from error

        raise CannotConnectError from error
    else:
        _LOGGER.debug("Connected to %s", data[CONF_HOST])

    return str(response["serNo"])


class KebaKeEnergyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for KEBA KeEnergy."""

    VERSION: int = CONFIG_ENTRY_VERSION

    def __init__(self) -> None:
        """Initialize flow."""
        self.host: str = ""
        self.ssl: bool = False
        self.serial_number: str | None = None

    async def _async_check_authentication_required(self) -> bool | None:
        """Check if authentication required."""
        session: ClientSession = async_get_clientsession(self.hass)
        has_authentication: bool = False

        try:
            async with session.get(f"http://{self.host}", allow_redirects=True) as response:
                if response.status == HTTPStatus.UNAUTHORIZED:
                    self.ssl = True
                    has_authentication = True
        except ClientError as error:
            _LOGGER.error("Client error %s", error)
            return None

        return has_authentication

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.host = user_input[CONF_HOST]
            has_authentication: bool | None = await self._async_check_authentication_required()

            if has_authentication is None:
                return self.async_abort(reason="cannot_connect")

            if has_authentication:
                return await self.async_step_auth(user_input)

            errors = await self._async_validate_or_error(user_input)

            if self.serial_number and not errors:
                return await self._async_complete_entry(user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "name": f"{MANUFACTURER} {NAME}",
                "host": self.host,
            },
        )

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
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        _LOGGER.debug("Discovery info: %s", discovery_info)

        self.host = discovery_info.hostname[0:-1]
        self.serial_number = discovery_info.properties["serialnumber"]

        await self.async_set_unique_id(self.serial_number)
        self._abort_if_unique_id_configured()

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle user-confirmation of discovered node."""
        errors: dict[str, str] = {}
        has_authentication: bool | None = await self._async_check_authentication_required()

        if has_authentication is None:
            return self.async_abort(reason="cannot_connect")

        if has_authentication:
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

    async def _async_validate_or_error(self, user_input: dict[str, Any]) -> dict[str, Any]:
        """Validate or error."""
        errors: dict[str, str] = {}

        try:
            self.serial_number = await validate_input(self.hass, data=user_input)
        except CannotConnectError:
            errors["base"] = "cannot_connect"
        except InvalidAuthError:
            errors["base"] = "invalid_auth"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        return errors

    async def _async_complete_entry(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        await self.async_set_unique_id(self.serial_number)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=f"{MANUFACTURER} {NAME} ({self.host})", data=user_input)


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuthError(HomeAssistantError):
    """Error to indicate there is invalid auth."""
