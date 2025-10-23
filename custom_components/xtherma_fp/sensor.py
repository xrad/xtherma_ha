"""The xtherma integration sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import XthermaDataUpdateCoordinator
from .entity import XthermaEntity
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


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """HA calls this to initialize sensor platform."""
    xtherma_data: XthermaData = config_entry.runtime_data

    _LOGGER.debug("Setup sensor platform")

    _initialize_sensors(xtherma_data, async_add_entities)

    return True


class XthermaBinarySensor(XthermaEntity, BinarySensorEntity):
    """Xtherma Binary Sensor."""

    # keep this for type safe access to custom members
    xt_description: XtBinarySensorEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self._coordinator.read_value(self.entity_description.key)
        if value is None:
            return
        self._attr_is_on = value > 0
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.xt_description.icon_provider:
            return self.xt_description.icon_provider(self.is_on)
        return super().icon


class XthermaSensor(XthermaEntity, SensorEntity):
    """Xtherma Value Sensor."""

    # keep this for type safe access to custom members
    xt_description: XtSensorEntityDescription

    def __init__(
        self,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtSensorEntityDescription,
    ) -> None:
        """Class Constructor."""
        super().__init__(coordinator, device_info, description)
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_state_class = description.state_class
        self._attr_options = description.options
        self._factor = description.factor

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


class XthermaEnumSensor(XthermaSensor):
    """Xtherma Enum Value Sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        options = self._attr_options
        if options is None:
            return
        value = self._coordinator.read_value(self.entity_description.key)
        if value is None:
            return
        index = int(value) % len(options)
        self._attr_native_value = options[index]
        self.async_write_ha_state()


class XthermaVersionSensor(XthermaSensor):
    """Xtherma Version Value Sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self._coordinator.read_value(self.entity_description.key)
        if value is None:
            return
        # note: input factor (assume: /100) has already been applied
        major = int(value)
        minor = int((value - major) * 100)
        self._attr_native_value = f"{major}.{minor:02d}"
        self.async_write_ha_state()
