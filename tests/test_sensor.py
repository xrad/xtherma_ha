"""Tests for the Xtherma sensor platform."""

from typing import cast
from unittest.mock import patch

import pytest
from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.const import Platform
from pytest_homeassistant_custom_component.common import snapshot_platform

from tests.conftest import MockModbusParam, MockModbusParamRegisters
from tests.helpers import (
    get_sensor_platform,
    provide_modbus_data,
    provide_rest_data,
)

from .conftest import init_integration, init_modbus_integration

SENSOR_ENTITY_ID_MODE = "sensor.test_entry_xtherma_config_current_operating_mode"
SENSOR_ENTITY_ID_SG = "sensor.test_entry_xtherma_config_sg_ready_status"
SENSOR_ENTITY_ID_LD1 = "sensor.test_entry_xtherma_config_ld1_fan_1_speed"
SENSOR_ENTITY_ID_CONTROLLER_V = "sensor.test_entry_xtherma_config_controller_version"
SENSOR_ENTITY_ID_MODBUS_TA = (
    "sensor.test_entry_xtherma_modbus_config_ta_outdoor_temperature"
)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_setup_sensor_rest_api(
    hass, entity_registry, snapshot, mock_rest_api_client
) -> None:
    """Test the setup of sensor platform using REST API."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SENSOR]):
        entry = await init_integration(hass, mock_rest_api_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_setup_sensor_modbus_tcp(
    hass, entity_registry, snapshot, mock_modbus_tcp_client
) -> None:
    """Test the setup of sensor platform using MODBUS TCP."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SENSOR]):
        entry = await init_modbus_integration(hass, mock_modbus_tcp_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_opmode_sensor_icon(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODE)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:thermometer-water"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_sgready_sensor_icon(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_SG)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:cancel"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_sensor_name(hass, mock_rest_api_client):
    """Check if regular sensors have proper (translated) names."""
    await init_integration(hass, mock_rest_api_client)
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_LD1)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "[LD1] Fan 1 speed"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_enum_sensor_name(hass, mock_rest_api_client):
    """Check if enum sensors have a proper (translated) names."""
    await init_integration(hass, mock_rest_api_client)
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODE)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "Current operating mode"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_version_sensor(hass, mock_rest_api_client):
    """Check if enum sensors have a proper (translated) names."""
    await init_integration(hass, mock_rest_api_client)
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
async def test_get_negative_number_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)
    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_TA)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SensorEntity)
    assert state.state == "-20.0"
