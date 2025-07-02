from custom_components.xtherma_fp.sensor_descriptors import SENSOR_DESCRIPTIONS
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
)


def test_xt_sensor_entity_description():
    desc_tvl = SENSOR_DESCRIPTIONS[0]
    assert desc_tvl is not None
    assert desc_tvl.key == "tvl"
    assert desc_tvl.native_unit_of_measurement == UnitOfTemperature.CELSIUS
    assert desc_tvl.device_class == SensorDeviceClass.TEMPERATURE
    assert desc_tvl.state_class == SensorStateClass.MEASUREMENT
    assert desc_tvl.factor == "/10"
