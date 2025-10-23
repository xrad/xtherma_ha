"""The xtherma integration numbers."""

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import XthermaDataUpdateCoordinator
from .entity import XthermaEntity
from .entity_descriptors import (
    XtNumberEntityDescription,
)
from .xtherma_data import XthermaData

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
    assert not xtherma_data.numbers_initialized  # noqa: S101

    coordinator = xtherma_data.coordinator

    assert coordinator is not None  # noqa: S101

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
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """HA calls this to initialize sensor platform."""
    xtherma_data: XthermaData = config_entry.runtime_data

    _LOGGER.debug("Setup number platform")

    _initialize_numbers(xtherma_data, async_add_entities)

    return True


class XthermaNumberEntity(XthermaEntity, NumberEntity):
    """Xtherma Number Input."""

    # keep this for type safe access to custom members
    xt_description: XtNumberEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self._coordinator.read_value(self.entity_description.key)
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
            await self._coordinator.async_write(self, value=value)
            self._attr_native_value = value
            self.async_write_ha_state()
        except HomeAssistantError:
            self._attr_force_update = True
            self.async_write_ha_state()
            self._attr_force_update = False
            raise
