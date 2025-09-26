"""The xtherma integration selects."""

import logging

from homeassistant.components.persistent_notification import async_create
from homeassistant.components.select import (
    SelectEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
)
from .coordinator import XthermaDataUpdateCoordinator
from .entity_descriptors import (
    XtSelectEntityDescription,
)
from .xtherma_data import XthermaData

_LOGGER = logging.getLogger(__name__)


# Create a sensor entity based on description.
def __build_select(
    desc: EntityDescription,
    coordinator: XthermaDataUpdateCoordinator,
    device_info: DeviceInfo,
) -> Entity | None:
    if isinstance(desc, XtSelectEntityDescription):
        return XthermaSelectEntity(coordinator, device_info, desc)
    return None


# Create and register sensor entities based on coordinator.data.
# Call site must ensure there is data and sensors are not already
# registered.
def _initialize_selects(
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback,
) -> None:
    assert not xtherma_data.selects_initialized  # noqa: S101

    coordinator = xtherma_data.coordinator

    assert coordinator is not None  # noqa: S101

    selects = []
    for key in coordinator.data:
        desc = coordinator.find_description(key)
        if not desc:
            _LOGGER.error("No select description found for key %s", key)
        else:
            select = __build_select(desc, coordinator, xtherma_data.device_info)
            if select:
                _LOGGER.debug('Adding select "%s"', desc.key)
                selects.append(select)
    _LOGGER.debug("Created %d selects", len(selects))
    async_add_entities(selects)

    xtherma_data.selects_initialized = True


# Initialize sensor entities if there is valid data in coordinator.
def _try_initialize_selects(
    hass: HomeAssistant,
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = xtherma_data.coordinator
    assert coordinator is not None  # noqa: S101
    if coordinator.data:
        _initialize_selects(xtherma_data, async_add_entities)
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

    _LOGGER.debug("Setup select platform")

    assert xtherma_data.coordinator is not None  # noqa: S101

    # Normally, __init__.py will have done an initial fetch and we should
    # have data in the coordinator to initialize the sensors.
    # If not (eg. because we just completed the config flow or the integration was
    # restarted too rapidly) we will try again in the listener.
    _try_initialize_selects(hass, xtherma_data, async_add_entities)

    @callback
    def _async_update_data() -> None:
        if not xtherma_data.selects_initialized:
            _try_initialize_selects(hass, xtherma_data, async_add_entities)

    # Note: data coordinators only fetch data as long as there is at least one
    # listener
    remove_fn = xtherma_data.coordinator.async_add_listener(_async_update_data)
    config_entry.async_on_unload(remove_fn)

    return True


class XthermaSelectEntity(CoordinatorEntity, SelectEntity):
    """Xtherma Select Input."""

    # keep this for type safe access to custom members
    xt_description: XtSelectEntityDescription

    def __init__(
        self,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtSelectEntityDescription,
    ) -> None:
        """Class Constructor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self.xt_description = description
        self._attr_has_entity_name = True
        if description.options is None:
            _LOGGER.error("Description of %s has no options!", description.key)
        else:
            self._attr_options = description.options
        self._attr_device_info = device_info
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self.entity_id = f"sensor.{self._attr_unique_id}"
        self.translation_key = description.key

    @property
    def current_option(self) -> str | None:
        """Return the option corresponding to the index in coordinator.data."""
        if self._coordinator.data:
            index = self._coordinator.data.get(self.entity_description.key, None)
            if type(index) is float:
                new_index = int(index) % len(self.options)
                self._attr_current_option = self.options[new_index]
                return self._attr_current_option
        return None

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.xt_description.icon_provider:
            return self.xt_description.icon_provider(self._attr_current_option)
        return super().icon

    async def async_select_option(self, option: str) -> None:
        """Set value."""
        index = self.options.index(option)
        await self._coordinator.async_write(self.xt_description, value=index)
        await self._coordinator.async_request_refresh()
