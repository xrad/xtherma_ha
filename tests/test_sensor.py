
import pytest
from tests.helpers import find_sensor_state, get_number_platform, get_sensor_platform, load_modbus_regs_from_json

from homeassistant.components.sensor import (
    SensorEntity,
)

async def test_binary_sensor_state(hass, init_integration):
    pk = find_sensor_state(hass, "pk")
    assert pk.state == "off"
    pww = find_sensor_state(hass, "pww")
    assert pww.state == "on"


async def test_binary_sensor_icon(hass, init_integration):
    platform = get_sensor_platform(hass)
    pk = find_sensor_state(hass, "pk")
    assert pk.state == "off"
    e_pk = platform.entities.get(pk.entity_id)
    assert e_pk is not None
    assert e_pk.icon == "mdi:pump-off"
    pww = find_sensor_state(hass, "pww")
    assert pww.state == "on"
    e_pww = platform.entities.get(pww.entity_id)
    assert e_pww is not None
    assert e_pww.icon == "mdi:pump"


async def test_opmode_sensor_icon(hass, init_integration):
    platform = get_sensor_platform(hass)
    state = find_sensor_state(hass, "mode")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:thermometer-water"


async def test_sgready_sensor_icon(hass, init_integration):
    platform = get_sensor_platform(hass)
    state = find_sensor_state(hass, "sg")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:cancel"


async def test_sensor_name(hass, init_integration):
    """Check if regular sensors have proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = find_sensor_state(hass, "ld1")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "[LD1] Fan 1 speed"


async def test_binary_sensor_name(hass, init_integration):
    """Check if binary sensors have a proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = find_sensor_state(hass, "pww")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "[PWW] Circulation pump hot water enabled"


async def test_enum_sensor_name(hass, init_integration):
    """Check if enum sensors have a proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = find_sensor_state(hass, "mode")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "Current operating mode"


async def test_version_sensor(hass, init_integration):
    """Check if enum sensors have a proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = find_sensor_state(hass, "controller_v")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.state == "2.39"


def load_and_prep_rest_response():
    regs_list = load_modbus_regs_from_json("rest_response.json")
    # change "ta" register #140 to be -20 °C in 2s complement
    regs_list[11][0] = ((20*10) ^ 65535) + 1
    return [
        regs_list
        # ([...]),x
        # ([...]),
    ]

@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    load_and_prep_rest_response(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
# check reading negative values from 2s complement
async def test_get_negative_number_modbus(hass, init_modbus_integration, mock_modbus_tcp_client):
    platform = get_sensor_platform(hass)
    state = find_sensor_state(hass, "ta")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SensorEntity)
    assert state.state == "-20.0"
