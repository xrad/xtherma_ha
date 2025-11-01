"""Tests for the Xtherma sensor platform."""

from typing import cast
from unittest.mock import patch

import pytest
from homeassistant.const import Platform
from pytest_homeassistant_custom_component.common import snapshot_platform

from tests.conftest import MockModbusParam, MockModbusParamRegisters
from tests.helpers import provide_modbus_data, provide_rest_data

from .conftest import init_integration, init_modbus_integration

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
    "mock_modbus_tcp_client", _test_get_negative_number_modbus_regs(), indirect=True
)
# check reading negative values from 2s complement
async def test_get_negative_number_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)

    state = hass.states.get(SENSOR_ENTITY_ID_MODBUS_TA)
    assert state.state == "-20.0"
