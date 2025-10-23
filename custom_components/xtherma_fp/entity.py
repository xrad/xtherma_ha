"Xtherma parent entity class."

import logging

from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from custom_components.xtherma_fp.const import EXTRA_STATE_ATTRIBUTE_PARAMETER

from .coordinator import XthermaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XthermaEntity(CoordinatorEntity):
    """Parent class for all entities assiciated with the Xtherma component."""

    xt_description: EntityDescription

    def __init__(
        self,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: EntityDescription,
    ) -> None:
        """Initialize the Xtherma entity."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self.xt_description = description
        self._attr_has_entity_name = True
        self._attr_device_info = device_info
        self._attr_device_class = description.device_class
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"
        self._attr_extra_state_attributes = {
            EXTRA_STATE_ATTRIBUTE_PARAMETER: self.xt_description.key,
        }
        self.translation_key = description.key
