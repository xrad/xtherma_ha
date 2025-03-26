"""Config flow for the xtherma integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .const import CONF_SERIAL_NUMBER, DOMAIN, FERNPORTAL_URL, LOGGER
from .xtherma_client import (
    XthermaClient,
    XthermaGeneralError,
    XthermaRateLimitError,
    XthermaTimeoutError,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY, msg="API Key"): str,
        vol.Required(CONF_SERIAL_NUMBER, msg="Serial Number (FP-XX-XXXXXX)"): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Check values in data dict."""
    api_key = data.get(CONF_API_KEY)
    serial_number = data.get(CONF_SERIAL_NUMBER)
    if not api_key or not serial_number:
        raise BadArguments

    if not serial_number.startswith("FP-"):
        raise BadArguments

    session = aiohttp_client.async_get_clientsession(hass)
    client = XthermaClient(
        url=FERNPORTAL_URL, api_key=api_key,
        serial_number=serial_number, session=session)

    await client.async_get_data()

    return {"title": "Xtherma"}


class XthermaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Process config flow."""

    VERSION = 1
    MINOR_VERSION = 0

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Process user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except BadArguments:
                LOGGER.debug("BadArguments")
                errors["base"] = "bad_arguments"
            except XthermaRateLimitError:
                LOGGER.debug("RateLimitError")
                errors["base"] = "rate_limit"
            except XthermaTimeoutError:
                LOGGER.debug("TimeoutError")
                errors["base"] = "timeout"
            except XthermaGeneralError:
                LOGGER.debug("GeneralError")
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                LOGGER.debug("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class BadArguments(HomeAssistantError):  # noqa: N818
    """User provided values are invalid."""
