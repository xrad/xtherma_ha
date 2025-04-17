"""The xtherma integration sensors."""

import logging
from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.components.persistent_notification import async_create
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import XthermaDataUpdateCoordinator
from .sensor_descriptors import (
    SENSOR_DESCRIPTIONS,
    XtBinarySensorEntityDescription,
    XtSensorEntityDescription,
)
from .xtherma_data import XthermaData

_LOGGER = logging.getLogger(__name__)

# Create a sensor entity based on description.
def __build_sensor(
        desc: EntityDescription,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo
        ) -> Entity | None:
    if isinstance(desc, XtBinarySensorEntityDescription):
        return XthermaBinarySensor(coordinator, device_info, desc)
    if isinstance(desc, XtSensorEntityDescription):
        return XthermaSensor(coordinator, device_info, desc)
    _LOGGER.error("Unsupported EntityDescription")
    return None

# Create and register sensor entities based on coordinator.data.
# Call site must ensure there is data and sensors are not already
# registerd.
def _initialize_sensors(
        xtherma_data: XthermaData,
        async_add_entities: AddEntitiesCallback
        ) -> None:
    assert(not xtherma_data.sensors_initialized)  # noqa: S101

    coordinator = xtherma_data.coordinator

    assert(coordinator is not None)  # noqa: S101

    _LOGGER.debug(f"Initialize {len(coordinator.data)} sensors")  # noqa: G004
    device_info = DeviceInfo(
        identifiers={(DOMAIN, xtherma_data.serial_fp)},
        name="Xtherma Wärmepumpe",
        manufacturer=MANUFACTURER,
        model=xtherma_data.serial_fp,
    )

    sensors = [ ]
    for key in coordinator.data:
        matching_descs_it = (
            d for d in SENSOR_DESCRIPTIONS if d.key.lower() == key.lower()
        )
        desc = next(matching_descs_it, None)
        if not desc:
            _LOGGER.error("No sensor description found for key %s", key)
        else:
            _LOGGER.debug('Adding sensor "%s"', desc.key)
            sensor = __build_sensor(desc, coordinator, device_info)
            if sensor:
                sensors.append(sensor)
    _LOGGER.debug("Created %d sensors", len(sensors))
    async_add_entities(sensors)

    xtherma_data.sensors_initialized = True

# Initialize sensor entities if there is valid data in coordinator.
def _try_initialize_sensors(
    hass: HomeAssistant,
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = xtherma_data.coordinator
    assert coordinator is not None  # noqa: S101
    if coordinator.data:
        _initialize_sensors(xtherma_data, async_add_entities)
    else:
        _LOGGER.debug("Data coordinator has no data yet, wait for next refresh")
        async_create(
            hass,
            "Xtherma",
            "Data coordinator has no data yet, wait for next refresh"
        )

def _delete_legacy_device(hass: HomeAssistant) -> None:
    _LOGGER.debug("Looking for legacy device in device registry")
    dev_reg = device_registry.async_get(hass)
    id_to_delete: str|None = None
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
    async_add_entities: AddEntitiesCallback
) -> bool:
    """HA calls this to initialize sensor platform."""
    xtherma_data: XthermaData = hass.data[DOMAIN][config_entry.entry_id]

    _LOGGER.debug("Setup sensor platform")

    assert xtherma_data.coordinator is not None  # noqa: S101

    # initial versions created DeviceInfo with a bad identifier - find and remove
    _delete_legacy_device(hass)

    # Normally, __init__.py will have done an initial fetch and we should
    # have data in the coordinator to initialize the sensors.
    # If not (eg. because we just completed the config flow or the integration was
    # restarted too rapidly) we will try again in the listener.
    _try_initialize_sensors(hass, xtherma_data, async_add_entities)

    @callback
    def _async_update_data() -> None:
        if not xtherma_data.sensors_initialized:
            _try_initialize_sensors(hass, xtherma_data, async_add_entities)

    # Note: data coordinators only fetch data as long as there is at least one
    # listener
    remove_fn = xtherma_data.coordinator.async_add_listener(_async_update_data)
    config_entry.async_on_unload(remove_fn)

    return True

class XthermaBinarySensor(BinarySensorEntity):
    """Xtherma Binary Sensor."""

    def __init__(self,
                 coordinator: DataUpdateCoordinator,
                 device_info: DeviceInfo,
                 description: XtBinarySensorEntityDescription) -> None:
        """Class Constructor."""
        self._coordinator = coordinator
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_device_class = description.device_class
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self.entity_id = f"sensor.{self._attr_unique_id}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self._coordinator.data:
            raw_value = self._coordinator.data.get(self.entity_description.key, None)
            if raw_value:
                return raw_value > 0
        return None

    """
    @property
    def icon(self):
        if self.state == STATE_ON:
            return "mdi:on"
        else:
            return "mdi:off"
    """

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._coordinator.last_update_success

class XthermaSensor(SensorEntity):
    """Xtherma Value Sensor."""

    def __init__(self,
                 coordinator: DataUpdateCoordinator,
                 device_info: DeviceInfo,
                 description: XtSensorEntityDescription) -> None:
        """Class Constructor."""
        self._coordinator = coordinator
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._factor = description.factor
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self.entity_id = f"sensor.{self._attr_unique_id}"

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the value reported by the sensor."""
        if self._coordinator.data:
            return self._coordinator.data.get(self.entity_description.key, None)
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._coordinator.last_update_success
