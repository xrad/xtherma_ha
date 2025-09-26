"""The xtherma integration numbers."""

import logging
from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.number import (
    NumberEntity,
)
from homeassistant.components.persistent_notification import async_create
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
)
from .coordinator import XthermaDataUpdateCoordinator
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
    for key in coordinator.data:
        desc = coordinator.find_description(key)
        if not desc:
            _LOGGER.error("No number description found for key %s", key)
        else:
            number = __build_number(desc, coordinator, xtherma_data.device_info)
            if number:
                _LOGGER.debug('Adding number "%s"', desc.key)
                numbers.append(number)
    _LOGGER.debug("Created %d numbers", len(numbers))
    async_add_entities(numbers)

    xtherma_data.numbers_initialized = True


# Initialize sensor entities if there is valid data in coordinator.
def _try_initialize_numbers(
    hass: HomeAssistant,
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = xtherma_data.coordinator
    assert coordinator is not None  # noqa: S101
    if coordinator.data:
        _initialize_numbers(xtherma_data, async_add_entities)
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

    _LOGGER.debug("Setup number platform")

    assert xtherma_data.coordinator is not None  # noqa: S101

    # Normally, __init__.py will have done an initial fetch and we should
    # have data in the coordinator to initialize the sensors.
    # If not (eg. because we just completed the config flow or the integration was
    # restarted too rapidly) we will try again in the listener.
    _try_initialize_numbers(hass, xtherma_data, async_add_entities)

    @callback
    def _async_update_data() -> None:
        if not xtherma_data.numbers_initialized:
            _try_initialize_numbers(hass, xtherma_data, async_add_entities)

    # Note: data coordinators only fetch data as long as there is at least one
    # listener
    remove_fn = xtherma_data.coordinator.async_add_listener(_async_update_data)
    config_entry.async_on_unload(remove_fn)

    return True


class XthermaNumberEntity(CoordinatorEntity, NumberEntity):
    """Xtherma Number Input."""

    # keep this for type safe access to custom members
    xt_description: XtNumberEntityDescription

    def __init__(
        self,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtNumberEntityDescription,
    ) -> None:
        """Class Constructor."""
        super().__init__(coordinator)
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
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the value reported by the sensor."""
        if self._coordinator.data:
            return self._coordinator.data.get(self.entity_description.key, None)
        return None

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.xt_description.icon_provider:
            return self.xt_description.icon_provider(self.native_value)
        return super().icon

    async def async_set_native_value(self, value: float) -> None:
        """Set value."""
        await self._coordinator.async_write(self.xt_description, value=value)
        # self._attr_is_on = True  # noqa: ERA001
        # self.async_write_ha_state()  # noqa: ERA001
        await self._coordinator.async_request_refresh()
