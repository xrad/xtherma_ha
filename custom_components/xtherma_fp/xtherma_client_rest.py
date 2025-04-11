"""Client to access Fernportal REST API."""

from datetime import UTC, datetime, timedelta

import aiohttp

from .const import FERNPORTAL_RATE_LIMIT_S, LOGGER
from .xtherma_client_common import (
    XthermaClient,
    XthermaGeneralError,
    XthermaRateLimitError,
    XthermaRestApiError,
    XthermaTimeoutError,
)


class XthermaClientRest(XthermaClient):
    """REST API access client."""

    def __init__(
        self, url: str, api_key: str, serial_number: str, session: aiohttp.ClientSession
    ) -> None:
        """Class constructor."""
        self._url = f"{url}/{serial_number}"
        self._api_key = api_key
        self._session = session

    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        return timedelta(seconds=FERNPORTAL_RATE_LIMIT_S)

    async def is_connected(self) -> bool:
        """Declare REST as always connected."""
        return True

    async def connect(self) -> None:
        """Not required for REST."""

    def _now(self) -> int:
        return int(datetime.now(UTC).timestamp())

    async def async_get_data(self) -> dict[str, dict]:
        """Obtain fresh data."""
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with self._session.get(self._url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as err:
            LOGGER.debug("API error: %s", err)
            if err.status == 429:  # noqa: PLR2004
                raise XthermaRateLimitError from err
            raise XthermaRestApiError(err.status) from err
        except TimeoutError as err:
            LOGGER.error("API request timed out")
            raise XthermaTimeoutError from err
        except Exception as err:
            LOGGER.error("Unknown API error: %s", err)
            raise XthermaGeneralError from err
