"""The xtherma integration sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import XthermaDataUpdateCoordinator, read_coordinator_value
from .entity_descriptors import (
    XtBinarySensorEntityDescription,
    XtSensorEntityDescription,
    XtVersionSensorEntityDescription,
)
from .xtherma_data import XthermaData

_LOGGER = logging.getLogger(__name__)


# Create a sensor entity based on description.
def __build_sensor(
    desc: EntityDescription,
    coordinator: XthermaDataUpdateCoordinator,
    device_info: DeviceInfo,
) -> Entity | None:
    if isinstance(desc, XtBinarySensorEntityDescription):
        return XthermaBinarySensor(coordinator, device_info, desc)
    if isinstance(desc, XtSensorEntityDescription):
        if desc.device_class == SensorDeviceClass.ENUM:
            return XthermaEnumSensor(coordinator, device_info, desc)
        if isinstance(desc, XtVersionSensorEntityDescription):
            return XthermaVersionSensor(coordinator, device_info, desc)
        return XthermaSensor(coordinator, device_info, desc)
    return None


# Create and register sensor entities based on coordinator.data.
# Call site must ensure there is data and sensors are not already
# registerd.
def _initialize_sensors(
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback,
) -> None:
    assert not xtherma_data.sensors_initialized  # noqa: S101

    coordinator = xtherma_data.coordinator

    assert coordinator is not None  # noqa: S101

    sensors = []
    descriptions = coordinator.get_entity_descriptions()
    for desc in descriptions:
        sensor = __build_sensor(desc, coordinator, xtherma_data.device_info)
        if sensor:
            _LOGGER.debug('Adding sensor "%s"', desc.key)
            sensors.append(sensor)
    _LOGGER.debug("Created %d sensors", len(sensors))
    async_add_entities(sensors)

    xtherma_data.sensors_initialized = True


def _delete_legacy_device(hass: HomeAssistant) -> None:
    _LOGGER.debug("Looking for legacy device in device registry")
    dev_reg = device_registry.async_get(hass)
    id_to_delete: str | None = None
    for device in dev_reg.devices.values():
        if device.manufacturer == MANUFACTURER and len(device.identifiers) == 1:
            (id1, id2) = device.identifiers.copy().pop()
            if id1 == DOMAIN and not id2:
                _LOGGER.debug(
                    "Deleting device = %s %s %s",
                    device.name,
                    device.id,
                    list(device.identifiers),
                )
                id_to_delete = device.id
                break
    if id_to_delete:
        dev_reg.async_remove_device(id_to_delete)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """HA calls this to initialize sensor platform."""
    xtherma_data: XthermaData = config_entry.runtime_data

    _LOGGER.debug("Setup sensor platform")

    # initial versions created DeviceInfo with a bad identifier - find and remove
    _delete_legacy_device(hass)

    _initialize_sensors(xtherma_data, async_add_entities)

    return True


class XthermaBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Xtherma Binary Sensor."""

    # keep this for type safe access to custom members
    xt_description: XtBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtBinarySensorEntityDescription,
    ) -> None:
        """Class Constructor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self.xt_description = description
        self._attr_has_entity_name = True
        self._attr_device_info = device_info
        self._attr_device_class = description.device_class
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"
        self.translation_key = description.key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = read_coordinator_value(self._coordinator, self.entity_description.key)
        self._attr_is_on = value > 0
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.xt_description.icon_provider:
            return self.xt_description.icon_provider(self.is_on)
        return super().icon


class XthermaSensor(CoordinatorEntity, SensorEntity):
    """Xtherma Value Sensor."""

    # keep this for type safe access to custom members
    xt_description: XtSensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtSensorEntityDescription,
    ) -> None:
        """Class Constructor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self.xt_description = description
        self._attr_has_entity_name = True
        self._attr_device_info = device_info
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_options = description.options
        self._factor = description.factor
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"
        self.translation_key = description.key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = read_coordinator_value(self._coordinator, self.entity_description.key)
        self._attr_native_value = value
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.xt_description.icon_provider:
            return self.xt_description.icon_provider(self.native_value)
        return super().icon


class XthermaEnumSensor(XthermaSensor):
    """Xtherma Enum Value Sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        options = self._attr_options
        if options is None:
            return
        value = read_coordinator_value(self._coordinator, self.entity_description.key)
        index = int(value) % len(options)
        self._attr_native_value = options[index]
        self.async_write_ha_state()


class XthermaVersionSensor(XthermaSensor):
    """Xtherma Version Value Sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = read_coordinator_value(self._coordinator, self.entity_description.key)
        # note: input factor (assume: /100) has already been applied
        major = int(value)
        minor = int((value - major) * 100)
        self._attr_native_value = f"{major}.{minor:02d}"
        self.async_write_ha_state()
