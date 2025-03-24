"""The xtherma integration sensors."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.sensor import (
    SensorEntity,
    EntityDescription
)
from homeassistant.components.persistent_notification import async_create
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import device_registry

from .xtherma_data import XthermaData
from .const import (
    LOGGER,
    DOMAIN, 
    MANUFACTURER,
)
from .sensor_descriptors import SENSOR_DESCRIPTIONS, XtSensorEntityDescription, XtBinarySensorEntityDescription
from .coordinator import XthermaDataUpdateCoordinator

# Create a sensor entity based on description.
def build_sensor(
        desc: EntityDescription, 
        coordinator: XthermaDataUpdateCoordinator, 
        device_info: DeviceInfo
        ) -> SensorEntity:
    if isinstance(desc, XtBinarySensorEntityDescription):
        return XthermaBinarySensor(coordinator, device_info, desc)
    if isinstance(desc, XtSensorEntityDescription):
        return XthermaSensor(coordinator, device_info, desc)
    raise Exception("Unsupported EntityDescription")

# Create and register sensor entities based on coordinator.data.
# Call site must ensure there is data and sensors are not already
# registerd.
def _initialize_sensors(
        xtherma_data: XthermaData,
        async_add_entities: AddEntitiesCallback
        ):
    assert(not xtherma_data.sensors_initialized)

    coordinator = xtherma_data.coordinator

    assert(coordinator.data is not None)

    LOGGER.debug(f"Initialize {len(coordinator.data)} sensors")
    device_info = DeviceInfo(
        identifiers={(DOMAIN, xtherma_data.serial_fp)},
        name="Xtherma Wärmepumpe",
        manufacturer=MANUFACTURER,
        model=xtherma_data.serial_fp,
    )

    sensors = [ ]
    for key in coordinator.data:
        desc = next((d for d in SENSOR_DESCRIPTIONS if d.key.lower() == key.lower()), None)
        if not desc:
            LOGGER.error(f"No sensor description found for key {key}")
        else:
            LOGGER.debug(f"Adding sensor {desc.key}")
            sensor = build_sensor(desc, coordinator, device_info)
            sensors.append(sensor)
    LOGGER.debug(f"Created {len(sensors)} sensors")
    async_add_entities(sensors)

    xtherma_data.sensors_initialized = True

# Initialize sensor entities if there is valid data in coordinator.
def _try_initialize_sensors(
    hass: HomeAssistant, 
    xtherma_data: XthermaData,
    async_add_entities: AddEntitiesCallback
):
    coordinator = xtherma_data.coordinator
    if coordinator.data:
        _initialize_sensors(xtherma_data, async_add_entities)
    else:
        LOGGER.debug("Data coordinator has no data yet, wait for next refresh")
        async_create(
            hass,
            "Xtherma",
            "Data coordinator has no data yet, wait for next refresh"
        )

def _delete_legacy_device(hass: HomeAssistant):
    LOGGER.debug("Looking for legacy device in device registry")
    dev_reg = device_registry.async_get(hass)
    id_to_delete: str|None = None
    for device in dev_reg.devices.values():
        if device.manufacturer == MANUFACTURER and len(device.identifiers) == 1:
            (id1, id2) = device.identifiers.copy().pop()
            if id1 == DOMAIN and not id2:
                LOGGER.debug(f"Deleting device = {device.name} {device.id} {list(device.identifiers)}")
                id_to_delete = device.id
                break
    if id_to_delete:
        dev_reg.async_remove_device(id_to_delete)

# HA calls this when sensor platform is initialized
async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> bool:
    xtherma_data: XthermaData = hass.data[DOMAIN][config_entry.entry_id]

    LOGGER.debug(f"Setup sensor platform")

    # initial versions created DeviceInfo with a bad identifier - find and remove
    _delete_legacy_device(hass)

    # Normally, __init__.py will have done an initial fetch and we should
    # have data in the coordinator to initialize the sensors.
    # If not (eg. because we just completed the config flow or the integration was 
    # restarted too rapidly) we will try again in the listener.
    _try_initialize_sensors(hass, xtherma_data, async_add_entities)

    @callback
    def _async_update_data():
        if not xtherma_data.sensors_initialized:
            _try_initialize_sensors(hass, xtherma_data, async_add_entities)

    # Note: data coordinators only fetch data as long as there is at least one
    # listener
    remove_fn = xtherma_data.coordinator.async_add_listener(_async_update_data)
    config_entry.async_on_unload(remove_fn)

    return True

class XthermaBinarySensor(BinarySensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, device_info: DeviceInfo, description: XtBinarySensorEntityDescription):
        self._coordinator = coordinator
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_device_class = description.device_class
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self.entity_id = f"sensor.{self._attr_unique_id}"

    @property
    def is_on(self) -> bool:
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
    def available(self):
        return self._coordinator.last_update_success

class XthermaSensor(SensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, device_info: DeviceInfo, description: XtSensorEntityDescription):
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
    def native_value(self):
        # LOGGER.warning(f"*** get native value of {self._attr_name} factor {self._factor}")
        if self._coordinator.data:
            raw_value = self._coordinator.data.get(self.entity_description.key, None)
            # if self._factor:
            #    return raw_value * self._factor
            return raw_value
        return None

    @property
    def available(self):
        return self._coordinator.last_update_success