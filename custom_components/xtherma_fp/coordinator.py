"""DataUpdater for Xtherma Fernportal cloud integration."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    FERNPORTAL_RATE_LIMIT_S,
    KEY_ENTRY_INPUT_FACTOR,
    KEY_ENTRY_KEY,
    KEY_ENTRY_UNIT,
    KEY_ENTRY_VALUE,
    KEY_TELEMETRY,
    LOGGER,
)
from .xtherma_client import XthermaClient, XthermaRateLimitError, XthermaTimeoutError

_FACTORS = {
    "*1000": 1000,
    "*100": 100,
    "*10": 10,
    "1000": 1000,
    "100": 100,
    "10": 10,
    "/1000": .001,
    "/100": .01,
    "/10": .1,
}

class XthermaDataUpdateCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """Regularly Fetches data from API client."""

    _client: XthermaClient

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: XthermaClient
    ) -> None:
        """Class constructor."""
        self._client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=FERNPORTAL_RATE_LIMIT_S),
        )

    async def _async_setup(self) -> None:
        """Set up the coordinator."""

    def _apply_input_factor(self, rawvalue: str, inputfactor: str) -> float:
        value = float(rawvalue)
        factor = _FACTORS.get(inputfactor, 1.0)
        return factor * value

    async def _async_update_data(self) -> dict[str, float]:
        result : dict[str, float] = {}
        try:
            LOGGER.debug("coordinator requesting new data")
            raw = await self._client.async_get_data()
            telemetry = raw[KEY_TELEMETRY]
            for entry in telemetry:
                key = entry.get(KEY_ENTRY_KEY, "").lower()
                rawvalue = entry.get(KEY_ENTRY_VALUE, None)
                inputfactor = entry.get(KEY_ENTRY_INPUT_FACTOR, None)
                if not key or not rawvalue:
                    LOGGER.error("entry has no 'key'")
                    continue
                value = self._apply_input_factor(rawvalue, inputfactor)
                result[key] = value
                if LOGGER.getEffectiveLevel() == logging.DEBUG:
                    rawvalue = entry[KEY_ENTRY_VALUE]
                    inputfactor = entry[KEY_ENTRY_INPUT_FACTOR]
                    unit = entry[KEY_ENTRY_UNIT]
                    LOGGER.debug(f'key="{key}" raw="{rawvalue}" value="{value}" unit="{unit}" inputfactor="{inputfactor}"')  # noqa: E501
        except XthermaRateLimitError as err:
            msg = "Error communicating with API, rate limiting"
            raise UpdateFailed(msg) from err
        except XthermaTimeoutError as err:
            msg = "Error communicating with API, time out"
            raise UpdateFailed(msg) from err
        except Exception as err:
            msg = "Error communicating with API, unknown reason"
            raise UpdateFailed(msg) from err
        LOGGER.debug(f"coordinator processed {len(result)}/{len(telemetry)} telemetry values")  # noqa: E501
        return result
