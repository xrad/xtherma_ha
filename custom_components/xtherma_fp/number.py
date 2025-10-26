"""The xtherma integration numbers."""

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import XthermaConfigEntry, XthermaData
from .coordinator import XthermaDataUpdateCoordinator
from .entity import XthermaCoordinatorEntity
from .entity_descriptors import (
    XtNumberEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


# Create a sensor entity based on description.
def __build_number(
    desc: EntityDescription,
    coordinator: XthermaDataUpdateCoordinator,
    device_info: DeviceInfo,
) -> Entity | None:
    if isinstance(desc, XtNumberEntityDescription):
        return XthermaNumberEntity(coordinator, device_info, desc)
    return None


# Create and register sensor entities based on coordinator.data.
# Call site must ensure there is data and sensors are not already
# registerd.
def _initialize_numbers(
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = xtherma_data.coordinator

    numbers = []
    for desc in coordinator.get_entity_descriptions():
        number = __build_number(desc, coordinator, xtherma_data.device_info)
        if number:
            _LOGGER.debug('Adding number "%s"', desc.key)
            numbers.append(number)
    _LOGGER.debug("Created %d numbers", len(numbers))
    async_add_entities(numbers)

    xtherma_data.numbers_initialized = True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: XthermaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """HA calls this to initialize sensor platform."""
    xtherma_data: XthermaData = config_entry.runtime_data

    _LOGGER.debug("Setup number platform")

    _initialize_numbers(xtherma_data, async_add_entities)

    return True


class XthermaNumberEntity(XthermaCoordinatorEntity, NumberEntity):
    """Xtherma Number Input."""

    # keep this for type safe access to custom members
    xt_description: XtNumberEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self.coordinator.read_value(self.entity_description.key)
        if value is None:
            return
        self._attr_native_value = value
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.xt_description.icon_provider:
            return self.xt_description.icon_provider(self.native_value)
        return super().icon

    async def async_set_native_value(self, value: float) -> None:
        """Set value."""
        try:
            await self.coordinator.async_write(self, value=value)
            self._attr_native_value = value
            self.async_write_ha_state()
        except HomeAssistantError:
            self._attr_force_update = True
            self.async_write_ha_state()
            self._attr_force_update = False
            raise
