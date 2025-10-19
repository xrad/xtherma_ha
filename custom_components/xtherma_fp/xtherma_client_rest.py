"""Client to access Fernportal REST API."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import aiohttp
from homeassistant.helpers.entity import EntityDescription

from custom_components.xtherma_fp.entity_descriptors import ENTITY_DESCRIPTIONS

from .const import (
    FERNPORTAL_RATE_LIMIT_S,
    KEY_SETTINGS,
    KEY_TELEMETRY,
)
from .xtherma_client_common import (
    XthermaClient,
    XthermaError,
    XthermaReadOnlyError,
    XthermaRestApiError,
    XthermaRestBusyError,
    XthermaTimeoutError,
)

_LOGGER = logging.getLogger(__name__)


class XthermaClientRest(XthermaClient):
    """REST API access client."""

    def __init__(
        self,
        url: str,
        api_key: str,
        serial_number: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Class constructor."""
        self._url = f"{url}/{serial_number}"
        self._api_key = api_key
        self._session = session

    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        return timedelta(seconds=FERNPORTAL_RATE_LIMIT_S)

    async def connect(self) -> None:
        """Not required for REST."""

    async def disconnect(self) -> None:
        """Not required for REST."""

    def _now(self) -> int:
        return int(datetime.now(UTC).timestamp())

    async def async_get_data(self) -> list[dict[str, Any]]:
        """Obtain fresh data."""
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with self._session.get(self._url, headers=headers) as response:
                response.raise_for_status()
                json_data: dict[str, Any] = await response.json()
                telemetry = json_data.get(KEY_TELEMETRY)
                if not isinstance(telemetry, list):
                    _LOGGER.error("Telemetry in REST API is not a list")
                    return []
                settings = json_data.get(KEY_SETTINGS)
                if not isinstance(settings, list):
                    _LOGGER.error("Settings in REST API is not a list")
                    return []
                telemetry.extend(settings)
                return telemetry
        except aiohttp.ClientResponseError as err:
            _LOGGER.debug("API error: %s", err)
            if err.status == 429:  # noqa: PLR2004
                raise XthermaRestBusyError from err
            raise XthermaRestApiError(err.status) from err
        except TimeoutError as err:
            _LOGGER.debug("API request timed out")
            raise XthermaTimeoutError from err
        except Exception as err:
            _LOGGER.debug("Unknown API error %s", err)
            raise XthermaError from err
        return []

    async def async_put_data(self, value: int, desc: EntityDescription) -> None:
        """Write data."""
        del value
        del desc
        _LOGGER.debug("Cannot write values using REST API connection")
        raise XthermaReadOnlyError

    def get_entity_descriptions(self) -> list[EntityDescription]:
        """Get all entity descriptions."""
        return ENTITY_DESCRIPTIONS
