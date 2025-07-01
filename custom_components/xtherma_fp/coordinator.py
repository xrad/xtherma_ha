"""DataUpdater for Xtherma Fernportal cloud integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    KEY_ENTRY_INPUT_FACTOR,
    KEY_ENTRY_KEY,
    KEY_ENTRY_UNIT,
    KEY_ENTRY_VALUE,
    KEY_TELEMETRY,
)
from .xtherma_client_common import (
    XthermaModbusError,
    XthermaNotConnectedError,
    XthermaRestApiError,
)
from .xtherma_client_rest import (
    XthermaClient,
    XthermaRateLimitError,
    XthermaTimeoutError,
)

_LOGGER = logging.getLogger(__name__)

_FACTORS = {
    "*1000": 1000,
    "*100": 100,
    "*10": 10,
    "1000": 1000,
    "100": 100,
    "10": 10,
    "/1000": 0.001,
    "/100": 0.01,
    "/10": 0.1,
}


class XthermaDataUpdateCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """Regularly Fetches data from API client."""

    _client: XthermaClient

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: XthermaClient,
    ) -> None:
        """Class constructor."""
        self._client = client
        update_interval = client.update_interval()
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def close(self) -> None:
        """Terminate usage."""
        _LOGGER.debug("Coordinator close")
        await self._client.disconnect()

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        _LOGGER.debug("Coordinator _async_setup")
        await self._client.connect()

    def _apply_input_factor(self, rawvalue: str, inputfactor: str) -> float:
        value = float(rawvalue)
        factor = _FACTORS.get(inputfactor, 1.0)
        return factor * value

    async def _async_update_data(self) -> dict[str, float]:  # noqa: C901
        result: dict[str, float] = {}
        try:
            _LOGGER.debug("Coordinator requesting new data")
            raw = await self._client.async_get_data()
            telemetry = raw[KEY_TELEMETRY]
            for entry in telemetry:
                key = entry.get(KEY_ENTRY_KEY, "").lower()
                rawvalue = entry.get(KEY_ENTRY_VALUE, None)
                inputfactor = entry.get(KEY_ENTRY_INPUT_FACTOR, None)
                if not key or not rawvalue:
                    _LOGGER.error("entry has no 'key'")
                    continue
                value = self._apply_input_factor(rawvalue, inputfactor)
                result[key] = value
                if _LOGGER.getEffectiveLevel() == logging.DEBUG:
                    rawvalue = entry[KEY_ENTRY_VALUE]
                    inputfactor = entry[KEY_ENTRY_INPUT_FACTOR]
                    unit = entry[KEY_ENTRY_UNIT]
                    _LOGGER.debug(
                        'key="%s" raw="%s" value="%s" unit="%s" inputfactor="%s"',
                        key,
                        rawvalue,
                        value,
                        unit,
                        inputfactor,
                    )
        except XthermaRateLimitError as err:
            msg = "Error communicating with API, rate limiting"
            raise UpdateFailed(msg) from err
        except XthermaTimeoutError as err:
            msg = "Error communicating with API, time out"
            raise UpdateFailed(msg) from err
        except XthermaNotConnectedError as err:
            msg = "No connection to server"
            raise UpdateFailed(msg) from err
        except XthermaRestApiError as err:
            msg = f"REST API error {err.code}"
            raise UpdateFailed(msg) from err
        except XthermaModbusError as err:
            msg = "Modbus error"
            raise UpdateFailed(msg) from err
        except Exception as err:
            msg = "Error communicating with API, unknown reason"
            raise UpdateFailed(msg) from err
        _LOGGER.debug(
            "coordinator processed %d/%d telemetry values",
            len(result),
            len(telemetry),
        )
        return result
