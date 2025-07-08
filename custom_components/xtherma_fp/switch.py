"""The xtherma integration switches."""

import logging
from typing import Any

from homeassistant.components.persistent_notification import async_create
from homeassistant.components.switch import (
    SwitchEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import XthermaDataUpdateCoordinator
from .sensor_descriptors import (
    XtSwitchEntityDescription,
)
from .xtherma_data import XthermaData

_LOGGER = logging.getLogger(__name__)


# Create a sensor entity based on description.
def __build_switch(
    desc: EntityDescription,
    coordinator: XthermaDataUpdateCoordinator,
    device_info: DeviceInfo,
) -> Entity | None:
    if isinstance(desc, XtSwitchEntityDescription):
        return XthermaSwitchEntity(coordinator, device_info, desc)
    return None


# Create and register sensor entities based on coordinator.data.
# Call site must ensure there is data and sensors are not already
# registerd.
def _initialize_switches(
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback,
) -> None:
    assert not xtherma_data.switches_initialized  # noqa: S101

    coordinator = xtherma_data.coordinator

    assert coordinator is not None  # noqa: S101

    _LOGGER.debug(f"Initialize {len(coordinator.data)} sensors")  # noqa: G004
    device_info = DeviceInfo(
        identifiers={(DOMAIN, xtherma_data.serial_fp)},
        name="Xtherma Wärmepumpe",
        manufacturer=MANUFACTURER,
        model=xtherma_data.serial_fp,
    )

    switches = []
    for key in coordinator.data:
        desc = coordinator.find_description(key)
        if not desc:
            _LOGGER.error("No switch description found for key %s", key)
        else:
            _LOGGER.debug('Adding switch "%s"', desc.key)
            switch = __build_switch(desc, coordinator, device_info)
            if switch:
                switches.append(switch)
    _LOGGER.debug("Created %d switches", len(switches))
    async_add_entities(switches)

    xtherma_data.switches_initialized = True


# Initialize sensor entities if there is valid data in coordinator.
def _try_initialize_switches(
    hass: HomeAssistant,
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = xtherma_data.coordinator
    assert coordinator is not None  # noqa: S101
    if coordinator.data:
        _initialize_switches(xtherma_data, async_add_entities)
    else:
        _LOGGER.debug("Data coordinator has no data yet, wait for next refresh")
        async_create(
            hass,
            "Xtherma",
            "Data coordinator has no data yet, wait for next refresh",
        )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """HA calls this to initialize sensor platform."""
    xtherma_data: XthermaData = config_entry.runtime_data

    _LOGGER.debug("Setup switch platform")

    assert xtherma_data.coordinator is not None  # noqa: S101

    # Normally, __init__.py will have done an initial fetch and we should
    # have data in the coordinator to initialize the sensors.
    # If not (eg. because we just completed the config flow or the integration was
    # restarted too rapidly) we will try again in the listener.
    _try_initialize_switches(hass, xtherma_data, async_add_entities)

    @callback
    def _async_update_data() -> None:
        if not xtherma_data.switches_initialized:
            _try_initialize_switches(hass, xtherma_data, async_add_entities)

    # Note: data coordinators only fetch data as long as there is at least one
    # listener
    remove_fn = xtherma_data.coordinator.async_add_listener(_async_update_data)
    config_entry.async_on_unload(remove_fn)

    return True


class XthermaSwitchEntity(SwitchEntity):
    """Xtherma Switch."""

    # keep this for type safe access to custom members
    xt_description: XtSwitchEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtSwitchEntityDescription,
    ) -> None:
        """Class Constructor."""
        self._coordinator = coordinator
        self.entity_description = description
        self.xt_description = description
        self._attr_has_entity_name = True
        self._attr_device_info = device_info
        self._attr_device_class = description.device_class
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self.entity_id = f"sensor.{self._attr_unique_id}"
        self.translation_key = description.key

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self._coordinator.data:
            raw_value = self._coordinator.data.get(self.entity_description.key, None)
            if raw_value is not None:
                return raw_value > 0
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._coordinator.last_update_success

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.xt_description.icon_provider:
            return self.xt_description.icon_provider(self.is_on)
        return super().icon

    def turn_on(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Turn the entity on."""

    def turn_off(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Turn the entity off."""
