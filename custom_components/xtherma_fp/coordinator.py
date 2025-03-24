"""
DataUpdater for Xtherma Fernportal cloud integration 
"""

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

import logging

from .xtherma_client import XthermaClient, RateLimitError, TimeoutError
from .const import (
    LOGGER,
    KEY_TELEMETRY, 
    DOMAIN, 
    FERNPORTAL_RATE_LIMIT_S, 
    KEY_ENTRY_VALUE,
    KEY_ENTRY_KEY,
    KEY_ENTRY_INPUT_FACTOR,
    KEY_ENTRY_UNIT,
)

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
    _client: XthermaClient = None
    
    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigEntry,
        client: XthermaClient
    ) -> None:
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
        pass

    def _apply_input_factor(self, rawvalue: str, inputfactor: str) -> float:
        value = float(rawvalue)
        factor = _FACTORS.get(inputfactor, 1.0)
        return factor * value

    async def _async_update_data(self) -> list[float]:
        try:
            LOGGER.debug(f"coordinator requesting new data")
            raw = await self._client.async_get_data()
            telemetry = raw[KEY_TELEMETRY]
            result = {}
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
                    LOGGER.debug(f"key=\"{key}\" raw=\"{rawvalue}\" value=\"{value}\" unit=\"{unit}\" inputfactor=\"{inputfactor}\"")
            LOGGER.debug(f"coordinator processed {len(result)}/{len(telemetry)} telemetry values")
            return result
        except RateLimitError:
            raise UpdateFailed(f"Error communicating with API, rate limiting")
        except TimeoutError:
            raise UpdateFailed(f"Error communicating with API, time out")
        except:
            raise UpdateFailed(f"Error communicating with API, unknown reason")
