"""The Xtherma integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import homeassistant.helpers.device_registry as dr
import homeassistant.helpers.entity_registry as er
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_API_KEY,
    CONF_HOST,
    CONF_PORT,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_CONNECTION,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
    MANUFACTURER,
    VERSION,
)
from .coordinator import XthermaDataUpdateCoordinator
from .xtherma_client_modbus import XthermaClientModbus
from .xtherma_client_rest import XthermaClientRest
from .xtherma_data import XthermaData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

_PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Initialize integration."""
    _LOGGER.debug("Setup integration")

    # setup global data - Note that subclassing ConfigEntry would be nicer for
    # type safety, but then the MockConfigEntry used in tests would be incompatible.
    xtherma_data = XthermaData()
    entry.runtime_data = xtherma_data

    serial_number = entry.data[CONF_SERIAL_NUMBER]
    xtherma_data.serial_fp = serial_number

    xtherma_data.device_info = dr.DeviceInfo(
        identifiers={(DOMAIN, xtherma_data.serial_fp)},
        name="Xtherma Wärmepumpe",
        manufacturer=MANUFACTURER,
        model=xtherma_data.serial_fp,
    )

    # create API client connector
    connection = entry.data.get(CONF_CONNECTION, CONF_CONNECTION_RESTAPI)
    if connection == CONF_CONNECTION_RESTAPI:
        api_key = entry.data[CONF_API_KEY]
        client = XthermaClientRest(
            url=FERNPORTAL_URL,
            api_key=api_key,
            serial_number=serial_number,
            session=async_get_clientsession(hass),
        )
    else:
        serial_number = entry.data[CONF_SERIAL_NUMBER]
        host = entry.data[CONF_HOST]
        port = entry.data[CONF_PORT]
        address = entry.data[CONF_ADDRESS]
        client = XthermaClientModbus(
            host=host,
            port=port,
            address=address,
        )

    # migrate entities
    await async_migrate_entities(hass, entry)

    # create data coordinator
    xtherma_data.coordinator = XthermaDataUpdateCoordinator(hass, entry, client)

    # initialize platforms
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    try:
        await xtherma_data.coordinator.async_config_entry_first_refresh()
    except Exception:  # noqa: BLE001
        _LOGGER.error("initial refresh failed")  # noqa: TRY400

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload integration."""
    _LOGGER.debug("Unload integration")
    xtherma_data: XthermaData = entry.runtime_data
    if xtherma_data and xtherma_data.coordinator:
        _LOGGER.debug("Close data coordinator")
        await xtherma_data.coordinator.close()
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def async_migrate_entry(_: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate config entry."""
    if config_entry.version > VERSION:
        _LOGGER.error("Downgrade not supported")
        return False

    if config_entry.version < VERSION:
        _LOGGER.debug(
            "Migrating configuration from version %s.%s",
            config_entry.version,
            config_entry.minor_version,
        )

    return True


async def async_migrate_entities(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> None:
    """Migrate entity registry."""
    device_registry = dr.async_get(hass)

    @callback
    def update_unique_id(entity_entry: er.RegistryEntry) -> dict[str, str] | None:
        """Update unique ID of entity entry."""
        device_id = entity_entry.device_id

        if entity_entry.unique_id.startswith(DOMAIN) and device_id is not None:
            device = device_registry.async_get(device_id)
            if device is not None and device.model is not None:
                return {
                    "new_unique_id": entity_entry.unique_id.replace(
                        f"{DOMAIN}_",
                        f"{str(device.model).lower()}-",
                    ),
                }
        return None

    await er.async_migrate_entries(hass, config_entry.entry_id, update_unique_id)
