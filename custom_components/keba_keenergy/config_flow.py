"""Config flow for KEBA KeEnergy."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any
from typing import TYPE_CHECKING

import voluptuous as vol
from aiohttp import ClientError
from homeassistant.config_entries import ConfigFlow
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.config_entries import OptionsFlowWithReload
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.const import CONF_SSL
from homeassistant.const import CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import NumberSelector
from homeassistant.helpers.selector import NumberSelectorConfig
from homeassistant.helpers.selector import NumberSelectorMode
from keba_keenergy_api.api import KebaKeEnergyAPI
from keba_keenergy_api.error import APIError

from .const import CONFIG_ENTRY_VERSION
from .const import CONF_BUFFER_TANK_TICK
from .const import CONF_EXTERNAL_HEAT_SOURCE_TICK
from .const import CONF_HEAT_CIRCUIT_TICK
from .const import CONF_HEAT_PUMP_TICK
from .const import CONF_HOT_WATER_TANK_TICK
from .const import CONF_SOLAR_CIRCUIT_TICK
from .const import CONF_SWITCH_VALVE_TICK
from .const import CONF_SYSTEM_TICK
from .const import DEFAULT_SCAN_INTERVAL
from .const import DEFAULT_SSL
from .const import DOMAIN
from .const import MANUFACTURER
from .const import MIN_SCAN_INTERVAL
from .const import NAME

if TYPE_CHECKING:
    from collections.abc import Mapping
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
    from aiohttp import ClientSession
    from .coordinator import KebaKeEnergyConfigEntry
    from .coordinator import KebaKeEnergyDataUpdateCoordinator

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

        self._entry: KebaKeEnergyConfigEntry | None = None

    async def _async_check_authentication_required(self) -> bool:
        """Check if authentication required."""
        session: ClientSession = async_get_clientsession(self.hass)
        has_authentication: bool = False

        try:
            async with session.get(f"https://{self.host}", ssl=False) as response:
                if response.status == HTTPStatus.UNAUTHORIZED:
                    self.ssl = True
                    has_authentication = True
        except ClientError as error:
            _LOGGER.debug(error)

        return has_authentication

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.host = user_input[CONF_HOST]
            has_authentication: bool = await self._async_check_authentication_required()

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
        _LOGGER.info("Discovery info: %s", discovery_info)

        self.host = discovery_info.hostname[0:-1]
        self.serial_number = discovery_info.properties["serialnumber"]

        await self.async_set_unique_id(self.serial_number)
        self._abort_if_unique_id_configured()

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle user-confirmation of discovered node."""
        errors: dict[str, str] = {}
        has_authentication: bool = await self._async_check_authentication_required()

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

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        self._entry = self._get_reconfigure_entry()

        self.host = self._entry.data[CONF_HOST]
        self.ssl = self._entry.data[CONF_SSL]

        return await self.async_step_user(user_input)

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
            errors["base"] = "unknown"
            _LOGGER.exception("Unexpected exception")

        return errors

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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: KebaKeEnergyConfigEntry,  # noqa: ARG004
    ) -> KebaKeEnergyOptionsFlow:
        """Get the options flow for this handler."""
        return KebaKeEnergyOptionsFlow()


class KebaKeEnergyOptionsFlow(OptionsFlowWithReload):
    """Option flow for KEBA KeEnergy."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        coordinator: KebaKeEnergyDataUpdateCoordinator | None = getattr(
            self.config_entry,
            "runtime_data",
            None,
        )

        if coordinator is None:
            return self.async_abort(reason="options_not_ready")

        schema_fields: dict[Any, Any] = {}

        schema_fields[
            vol.Required(
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

        schema_fields[
            vol.Required(
                CONF_SYSTEM_TICK,
                default=self.config_entry.options.get(CONF_SYSTEM_TICK, 1),
            )
        ] = NumberSelector(
            NumberSelectorConfig(
                min=1,
                max=180,
                step=1,
                mode=NumberSelectorMode.BOX,
            ),
        )

        tick_mapping: dict[str, str] = {
            CONF_HEAT_PUMP_TICK: "heat_pump",
            CONF_HEAT_CIRCUIT_TICK: "heat_circuit",
            CONF_SOLAR_CIRCUIT_TICK: "solar_circuit",
            CONF_HOT_WATER_TANK_TICK: "hot_water_tank",
            CONF_BUFFER_TANK_TICK: "buffer_tank",
            CONF_SWITCH_VALVE_TICK: "switch_valve",
            CONF_EXTERNAL_HEAT_SOURCE_TICK: "external_heat_source",
        }

        for conf_key, position_attr in tick_mapping.items():
            if getattr(coordinator.position, position_attr):
                schema_fields[
                    vol.Required(
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
            data_schema=vol.Schema(schema_fields),
        )


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuthError(HomeAssistantError):
    """Error to indicate there is invalid auth."""
