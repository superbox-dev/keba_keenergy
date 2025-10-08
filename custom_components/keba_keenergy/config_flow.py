"""Config flow for KEBA KeEnergy."""

import logging
from http import HTTPStatus
from typing import Any
from typing import TYPE_CHECKING

import voluptuous as vol
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
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
    },
)

STEP_DISCOVERY_CONFIRM_DATA_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
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

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            serial_number, errors = await self._async_validate_or_error(user_input)
            self.host = user_input[CONF_HOST]

            if serial_number and not errors:
                await self.async_set_unique_id(serial_number)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"{MANUFACTURER} {NAME} ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "name": f"{MANUFACTURER} {NAME}",
                "host": self.host,
            },
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        _LOGGER.debug("Starting discovery via: %s", discovery_info)

        self.host = discovery_info.hostname[0:-1]
        serial_number = discovery_info.properties["serialnumber"]

        _LOGGER.debug("Discovery info: %s", discovery_info)

        await self.async_set_unique_id(serial_number)
        self._abort_if_unique_id_configured()

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle user-confirmation of discovered node."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_HOST] = self.host
            _, errors = await self._async_validate_or_error(user_input)

            if not errors:
                return self.async_create_entry(
                    title=f"{MANUFACTURER} {NAME} ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="discovery_confirm",
            data_schema=STEP_DISCOVERY_CONFIRM_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "name": f"{MANUFACTURER} {NAME}",
                "host": self.host,
            },
        )

    async def _async_validate_or_error(self, user_input: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Validate or error."""
        errors: dict[str, str] = {}
        serial_number: str = ""

        try:
            serial_number = await validate_input(self.hass, data=user_input)
        except CannotConnectError:
            errors["base"] = "cannot_connect"
        except InvalidAuthError:
            errors["base"] = "invalid_auth"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        return serial_number, errors


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuthError(HomeAssistantError):
    """Error to indicate there is invalid auth."""
