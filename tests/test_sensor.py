"""Tests for the Xtherma sensor platform."""

from typing import cast

import pytest
from homeassistant.components.sensor import (
    SensorEntity,
)

from tests.conftest import MockModbusParam, MockModbusParamRegisters
from tests.helpers import (
    get_sensor_platform,
    provide_modbus_data,
    provide_rest_data,
)

SENSOR_ENTITY_ID_MODE = "sensor.test_entry_xtherma_config_current_operating_mode"
SENSOR_ENTITY_ID_SG = "sensor.test_entry_xtherma_config_sg_ready_status"
SENSOR_ENTITY_ID_LD1 = "sensor.test_entry_xtherma_config_ld1_fan_1_speed"
SENSOR_ENTITY_ID_CONTROLLER_V = "sensor.test_entry_xtherma_config_controller_version"
SENSOR_ENTITY_ID_MODBUS_TA = (
    "sensor.test_entry_xtherma_modbus_config_ta_outdoor_temperature"
)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_opmode_sensor_icon(hass, init_integration):
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODE)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:thermometer-water"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_sgready_sensor_icon(hass, init_integration):
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_SG)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:cancel"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_sensor_name(hass, init_integration):
    """Check if regular sensors have proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_LD1)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "[LD1] Fan 1 speed"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_enum_sensor_name(hass, init_integration):
    """Check if enum sensors have a proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODE)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "Current operating mode"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_version_sensor(hass, init_integration):
    """Check if enum sensors have a proper (translated) names."""
    await hass.config.async_load()
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_CONTROLLER_V)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.state == "2.43"


def _test_get_negative_number_modbus_regs() -> list[MockModbusParam]:
    param = provide_modbus_data()
    regs_list = param[0]
    # change "ta" register #140 to be -20 °C in 2s complement
    regs: MockModbusParamRegisters = cast(
        "MockModbusParamRegisters", regs_list[11]["registers"]
    )
    regs[0] = ((20 * 10) ^ 65535) + 1
    return [regs_list]


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    _test_get_negative_number_modbus_regs(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
# check reading negative values from 2s complement
async def test_get_negative_number_modbus(hass, init_modbus_integration):
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_TA)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SensorEntity)
    assert state.state == "-20.0"
