"""Config flow for the xtherma integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigError,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_ADDRESS, CONF_API_KEY, CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
)
from .xtherma_client_modbus import XthermaClientModbus
from .xtherma_client_rest import (
    XthermaClientRest,
    XthermaGeneralError,
    XthermaRateLimitError,
    XthermaTimeoutError,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_rest_api(
    hass: HomeAssistant,
    data: dict[str, Any],
    errors: dict[str, str],
) -> bool:
    api_key = data.get(CONF_API_KEY)
    serial_number = data.get(CONF_SERIAL_NUMBER)
    if not api_key or not serial_number:
        errors["base"] = "bad_arguments"
        return False

    if not serial_number.startswith("FP-"):
        errors["base"] = "bad_arguments"
        return False

    try:
        session = aiohttp_client.async_get_clientsession(hass)
        client = XthermaClientRest(
            url=FERNPORTAL_URL,
            api_key=api_key,
            serial_number=serial_number,
            session=session,
        )
        await client.async_get_data()
    except XthermaRateLimitError:
        _LOGGER.debug("RateLimitError")
        errors["base"] = "rate_limit"
    except XthermaTimeoutError:
        _LOGGER.debug("TimeoutError")
        errors["base"] = "timeout"
    except XthermaGeneralError:
        _LOGGER.debug("GeneralError")
        errors["base"] = "cannot_connect"
    except Exception:  # noqa: BLE001
        _LOGGER.debug("Unexpected exception")
        errors["base"] = "unknown"
    else:
        return True

    return False


async def _validate_modbus_tcp(
    hass: HomeAssistant,  # noqa: ARG001
    data: dict[str, Any],
    errors: dict[str, str],
) -> bool:
    """Check values in data dict."""
    host = data.get(CONF_HOST)
    port = data.get(CONF_PORT)
    address = data.get(CONF_ADDRESS)
    if not host or not port or not address:
        errors["base"] = "bad_arguments"
        return False

    if int(port) != port or int(address) != address:
        errors["base"] = "bad_arguments"
        return False

    try:
        client = XthermaClientModbus(
            host=host,
            port=port,
            address=address,
        )
        await client.async_get_data()
    except XthermaTimeoutError:
        _LOGGER.debug("TimeoutError")
        errors["base"] = "timeout"
    except XthermaGeneralError:
        _LOGGER.debug("GeneralError")
        errors["base"] = "cannot_connect"
    except Exception:  # noqa: BLE001
        _LOGGER.debug("Unexpected exception")
        errors["base"] = "unknown"
    else:
        return True

    return False


async def _get_title() -> str:
    return "Xtherma"


class XthermaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Process config flow."""

    VERSION = 1
    MINOR_VERSION = 0

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process user step."""
        if user_input is not None:
            connection_type = user_input[CONF_CONNECTION]
            if connection_type == CONF_CONNECTION_RESTAPI:
                return await self.async_step_rest_api()
            if connection_type == CONF_CONNECTION_MODBUSTCP:
                return await self.async_step_modbus_tcp()

        schema = vol.Schema(
            {
                vol.Required(CONF_CONNECTION): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            CONF_CONNECTION_RESTAPI,
                            # CONF_CONNECTION_MODBUSTCP
                        ],
                        mode=SelectSelectorMode.LIST,
                        translation_key=CONF_CONNECTION,
                    ),
                ),
            },
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_rest_api(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process rest api config step."""
        errors: dict[str, str] = {}

        if user_input is not None and await _validate_rest_api(
            self.hass,
            user_input,
            errors,
        ):
            # also store connection type collected in async_step_user()
            user_input[CONF_CONNECTION] = CONF_CONNECTION_RESTAPI
            title = await _get_title()
            return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY, msg="API Key"): str,
                vol.Required(
                    CONF_SERIAL_NUMBER,
                    msg="Serial Number (FP-XX-XXXXXX)",
                ): str,
            },
        )

        return self.async_show_form(
            step_id="rest_api",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_modbus_tcp(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process modbus tcp config step."""
        errors: dict[str, str] = {}

        if user_input is not None and await _validate_modbus_tcp(
            self.hass,
            user_input,
            errors,
        ):
            # also store connection type collected in async_step_user()
            user_input[CONF_CONNECTION] = CONF_CONNECTION_MODBUSTCP
            title = await _get_title()
            return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=10001): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=0, max=65535),
                ),
                vol.Required(CONF_ADDRESS, default=33): NumberSelector(
                    NumberSelectorConfig(min=1, max=255, mode=NumberSelectorMode.BOX),
                ),
            },
        )

        return self.async_show_form(
            step_id="modbus_tcp",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,  # noqa: ARG004
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler()


class OptionsFlowHandler(OptionsFlow):
    """Reconfigure integration."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Manage the options."""
        connection = self.config_entry.data.get(
            CONF_CONNECTION,
            CONF_CONNECTION_RESTAPI,
        )
        if connection == CONF_CONNECTION_RESTAPI:
            return await self.async_step_rest_api()
        if connection == CONF_CONNECTION_MODBUSTCP:
            return await self.async_step_modbus_tcp()

        raise ConfigError

    async def async_step_rest_api(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process rest api config step."""
        errors: dict[str, str] = {}

        hass = self.hass
        entry = self.config_entry

        if user_input is not None:
            user_input[CONF_CONNECTION] = CONF_CONNECTION_RESTAPI
            hass.config_entries.async_update_entry(entry, data=user_input)
            await hass.config_entries.async_reload(entry.entry_id)
            return self.async_create_entry(data={})

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_API_KEY,
                    msg="API Key",
                    default=entry.data[CONF_API_KEY],
                ): str,
                vol.Required(
                    CONF_SERIAL_NUMBER,
                    msg="Serial Number (FP-XX-XXXXXX)",
                    default=entry.data[CONF_SERIAL_NUMBER],
                ): str,
            },
        )

        return self.async_show_form(
            step_id="rest_api",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_modbus_tcp(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process modbus tcp config step."""
        errors: dict[str, str] = {}

        hass = self.hass
        entry = self.config_entry

        if user_input is not None:
            user_input[CONF_CONNECTION] = CONF_CONNECTION_MODBUSTCP
            hass.config_entries.async_update_entry(entry, data=user_input)
            await hass.config_entries.async_reload(entry.entry_id)
            return self.async_create_entry(data={})

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
                vol.Required(CONF_PORT, default=entry.data[CONF_PORT]): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=0, max=65535),
                ),
                vol.Required(
                    CONF_ADDRESS,
                    default=entry.data[CONF_ADDRESS],
                ): NumberSelector(
                    NumberSelectorConfig(min=1, max=255, mode=NumberSelectorMode.BOX),
                ),
            },
        )

        return self.async_show_form(
            step_id="modbus_tcp",
            data_schema=schema,
            errors=errors,
        )
