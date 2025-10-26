"""The Xtherma integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
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

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

_PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT]


@dataclass
class XthermaData:
    """Global data for integration."""

    coordinator: XthermaDataUpdateCoordinator
    sensors_initialized: bool
    switches_initialized: bool
    numbers_initialized: bool
    selects_initialized: bool
    serial_fp: str
    device_info: dr.DeviceInfo


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Initialize integration."""
    _LOGGER.debug("Setup integration")
    serial_number = entry.data[CONF_SERIAL_NUMBER]

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

    coordinator = XthermaDataUpdateCoordinator(hass, entry, client)
    device_info = dr.DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer=MANUFACTURER,
        model=serial_number,
    )

    entry.runtime_data = XthermaData(
        coordinator=coordinator,
        sensors_initialized=False,
        switches_initialized=False,
        numbers_initialized=False,
        selects_initialized=False,
        serial_fp=serial_number,
        device_info=device_info,
    )

    # migrate entities
    await async_migrate_devices(hass, entry)
    await async_migrate_entities(hass, entry)

    # Try updating data from the client. This can fail, and an exception
    # will be thrown, causing HA to retry this entire setup after a while.
    try:
        await coordinator.async_config_entry_first_refresh()
    except:
        await coordinator.close()
        raise

    # initialize platforms
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    # make sure entities immediately have a valid state
    coordinator.async_update_listeners()

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


async def async_migrate_devices(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> None:
    """Migrate device registry."""
    registry = dr.async_get(hass)
    for device_entry in dr.async_entries_for_config_entry(
        registry, config_entry.entry_id
    ):
        if device_entry.identifiers != {(DOMAIN, config_entry.entry_id)}:
            registry.async_update_device(
                device_entry.id, new_identifiers={(DOMAIN, config_entry.entry_id)}
            )


async def async_migrate_entities(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> None:
    """Migrate entity registry."""

    @callback
    def update_unique_id(entity_entry: er.RegistryEntry) -> dict[str, str] | None:
        """Update unique ID of entity entry."""
        if entity_entry.unique_id.startswith(DOMAIN):
            return {
                "new_unique_id": entity_entry.unique_id.replace(
                    f"{DOMAIN}_",
                    f"{config_entry.entry_id}-",
                ),
            }

        return None

    await er.async_migrate_entries(hass, config_entry.entry_id, update_unique_id)

    registry = er.async_get(hass)
    for entity_entry in er.async_entries_for_config_entry(
        registry,
        config_entry.entry_id,
    ):
        if entity_entry.suggested_object_id is not None:
            _LOGGER.debug(
                "remove suggested_object_id from entity entry %s",
                entity_entry.unique_id,
            )
            registry.async_remove(entity_entry.entity_id)
            registry.async_get_or_create(
                entity_entry.domain,
                entity_entry.platform,
                entity_entry.unique_id,
                config_entry=config_entry,
                device_id=entity_entry.device_id,
            )
