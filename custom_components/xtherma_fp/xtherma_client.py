"""REST API client for Xtherma Fernportal cloud integration."""

import datetime
import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)


class XthermaRateLimitError(Exception):
    """Exception indicating REST API was accessed to frequently."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("API is busy")


class XthermaGeneralError(Exception):
    """Exception indicating a general error."""

    def __init__(self, code: int) -> None:
        """Class constructor."""
        super().__init__("General error")
        self.code = code


class XthermaTimeoutError(Exception):
    """Exception indicating a communication timeout."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("timeout")


class XthermaClient:
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

    def _now(self) -> int:
        return int(datetime.datetime.now(datetime.UTC).timestamp())

    async def async_get_data(self) -> dict[str, dict]:
        """Obtain fresh data."""
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with self._session.get(self._url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as err:
            _LOGGER.debug("API error: %s", err)
            if err.status == 429:  # noqa: PLR2004
                raise XthermaRateLimitError from err
            raise XthermaGeneralError(err.status) from err
        except TimeoutError as err:
            _LOGGER.exception("API request timed out")
            raise XthermaTimeoutError from err
        except Exception as err:
            _LOGGER.exception("Unknown API error: %s")
            raise XthermaGeneralError(0) from err
