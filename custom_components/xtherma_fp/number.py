"""The xtherma integration numbers."""

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import XthermaConfigEntry
from .entity import XthermaCoordinatorEntity
from .entity_descriptors import XtNumberEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: XthermaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """HA calls this to initialize sensor platform."""
    _LOGGER.debug("Setup number platform")
    xtherma_data = config_entry.runtime_data
    coordinator = xtherma_data.coordinator

    numbers = []
    for desc in coordinator.get_entity_descriptions():
        if not isinstance(desc, XtNumberEntityDescription):
            continue
        _LOGGER.debug('Adding number "%s"', desc.key)
        numbers.append(XthermaNumberEntity(coordinator, xtherma_data.device_info, desc))

    _LOGGER.debug("Created %d numbers", len(numbers))
    async_add_entities(numbers)
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
