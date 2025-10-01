"""DataUpdater for Xtherma Fernportal cloud integration."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.xtherma_fp.entity_descriptors import XtSensorEntityDescription

from .const import (
    DOMAIN,
    KEY_ENTRY_INPUT_FACTOR,
    KEY_ENTRY_KEY,
    KEY_ENTRY_VALUE,
)
from .xtherma_client_common import (
    XthermaBusyError,
    XthermaModbusError,
    XthermaNotConnectedError,
    XthermaReadOnlyError,
    XthermaRestApiError,
)
from .xtherma_client_rest import (
    XthermaClient,
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

_RFACTORS = {
    "*1000": 0.001,
    "*100": 0.01,
    "*10": 0.1,
    "1000": 0.001,
    "100": 0.01,
    "10": 0.1,
    "/1000": 1000,
    "/100": 100,
    "/10": 10,
}

# Time in seconds the device needs to process a write request.
# During this time, we block reads which would potentially restore
# the old value.
_WRITE_SETTLE_TIME_S = 30


@dataclass
class _PendingWrite:
    value: float
    blocked_until: datetime


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
        self._pending_writes: dict[str, _PendingWrite] = {}
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

    def _apply_input_factor(self, rawvalue: str, inputfactor: str | None) -> float:
        value = float(rawvalue)
        if not isinstance(inputfactor, str):
            return value
        factor = _FACTORS.get(inputfactor, 1.0)
        return factor * value

    async def _async_update_data(self) -> dict[str, float]:
        result: dict[str, float] = {}
        try:
            _LOGGER.debug("Coordinator requesting new data")
            client_data = await self._client.async_get_data()
            for entry in client_data:
                key = entry.get(KEY_ENTRY_KEY, "").lower()
                pending_write = self._is_blocked(key)
                if pending_write is not None:
                    result[key] = pending_write
                    _LOGGER.debug(
                        'Skipping update of key="%s" due to pending write',
                        key,
                    )
                else:
                    rawvalue = entry.get(KEY_ENTRY_VALUE, None)
                    inputfactor = entry.get(KEY_ENTRY_INPUT_FACTOR, None)
                    if key is None or rawvalue is None:
                        _LOGGER.error("entry incomplete: %s", entry)
                        continue
                    value = self._apply_input_factor(rawvalue, inputfactor)
                    result[key] = value
                    _LOGGER.debug(
                        'key="%s" raw="%s" value="%s" inputfactor="%s"',
                        key,
                        rawvalue,
                        value,
                        inputfactor,
                    )
        except XthermaBusyError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="read_busy_error",
            ) from err
        except XthermaTimeoutError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="timeout_error",
            ) from err
        except XthermaNotConnectedError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="not_connected_error",
            ) from err
        except XthermaRestApiError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="rest_api_error",
                translation_placeholders={
                    "error": str(err),
                },
            ) from err
        except XthermaModbusError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="modbus_read_error",
                translation_placeholders={
                    "error": str(err),
                },
            ) from err
        except Exception as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="general_error",
            ) from err
        _LOGGER.debug(
            "coordinator processed %d/%d values",
            len(result),
            len(client_data),
        )
        return result

    def get_entity_descriptions(self) -> list[EntityDescription]:
        """Get all entity descriptions."""
        if self._client is not None:
            return self._client.get_entity_descriptions()
        return []

    def _block_for(self, key: str, seconds: int, value: float) -> None:
        """Block reads for a specific register for N seconds."""
        _LOGGER.debug("Block reads of key %s for %d seconds", key, seconds)
        self._pending_writes[key] = _PendingWrite(
            blocked_until=datetime.now(UTC) + timedelta(seconds=seconds),
            value=value,
        )

    def _is_blocked(self, key: str) -> float | None:
        """Test if device-side processing for key is in progress."""
        # check if any keys are blocked
        if not self._pending_writes:
            return None
        # check if our key might be blocked
        pending = self._pending_writes.get(key)
        if pending is None:
            return None
        now = datetime.now(UTC)
        if now > pending.blocked_until:
            # block time expired, delete key
            self._pending_writes.pop(key)
            return None
        # key is actually blocked
        return pending.value

    def _reverse_apply_input_factor(self, value: float, inputfactor: str | None) -> int:
        if not isinstance(inputfactor, str):
            return int(value)
        factor = _RFACTORS.get(inputfactor, 1.0)
        return int(factor * value)

    async def async_write(self, entity: Entity, value: float) -> None:
        """Add a write request to the queue."""
        desc = entity.entity_description
        try:
            if isinstance(desc, XtSensorEntityDescription):
                int_value = self._reverse_apply_input_factor(value, desc.factor)
            else:
                int_value = int(value)
            await self._client.async_put_data(desc=desc, value=int_value)
            self._block_for(key=desc.key, seconds=_WRITE_SETTLE_TIME_S, value=value)
        except XthermaReadOnlyError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="read_only_error",
                translation_placeholders={
                    "entity_id": entity.entity_id,
                },
            ) from err
        except XthermaBusyError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_busy_error",
                translation_placeholders={
                    "entity_id": entity.entity_id,
                },
            ) from err
        except XthermaModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="modbus_write_error",
                translation_placeholders={
                    "error": str(err),
                    "entity_id": entity.entity_id,
                },
            ) from err


def read_coordinator_value(coordinator: DataUpdateCoordinator, key: str) -> int | float:
    """Read a value from us."""
    if coordinator.data is None:
        msg = "No data in coordinator"
        raise HomeAssistantError(msg)
    value = coordinator.data.get(key, None)
    if not isinstance(value, (int, float)):
        msg = "Illegal data in coordinator key=%s value=<%s>"
        raise HomeAssistantError(msg, key, value)
    return value
