from math import e
from unittest.mock import Mock, patch
import pytest
from unittest.mock import AsyncMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_HOST, CONF_PORT
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
)
from homeassistant.core import State

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_SERIAL_NUMBER,
    DOMAIN,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from custom_components.xtherma_fp.sensor_descriptors import MODBUS_SENSORS_COOLING_CURVE_1, MODBUS_SENSORS_COOLING_CURVE_2, MODBUS_SENSORS_GENERAL_STATE, MODBUS_SENSORS_HEATING_CONTROL, MODBUS_SENSORS_HEATING_CURVE_1, MODBUS_SENSORS_HEATING_CURVE_2, MODBUS_SENSORS_HEATING_STATE, MODBUS_SENSORS_HOT_WATER, MODBUS_SENSORS_HYDRAULIC_CIRCUIT, MODBUS_SENSORS_NETWORK, MODBUS_SENSORS_PERFORMANCE, MODBUS_SENSORS_POWER, MODBUS_SENSORS_TEMPERATURES
from custom_components.xtherma_fp.xtherma_data import XthermaData
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from tests.const import MOCK_MODBUS_ADDRESS, MOCK_MODBUS_HOST, MOCK_MODBUS_PORT, MOCK_SERIAL_NUMBER


def _verify_entry(entry: ConfigEntry):
    assert isinstance(entry.runtime_data, XthermaData)


def _find_state(states: list[State], id: str) -> State | None:
    for s in states:
        if s.entity_id == id:
            return s
    return None


def _verify_sensors(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.sensors_initialized

    our_sensor_states = [
        state
        for state in hass.states.async_all("sensor")
        if state.entity_id.startswith("sensor.xtherma_fp")
    ]
    assert len(our_sensor_states) == 43

    # check some entities
    state = _find_state(our_sensor_states, "sensor.xtherma_fp_system_active")
    assert state is not None
    assert state.state == "on"
    assert state.attributes["device_class"] == BinarySensorDeviceClass.POWER

from pymodbus.client import AsyncModbusTcpClient

MODBUS_CLIENT_PATH = "custom_components.xtherma_fp.xtherma_client_modbus.AsyncModbusTcpClient"

@pytest.fixture
async def mock_modbus_tcp_client(request):
    with patch(MODBUS_CLIENT_PATH) as MockModbusClient:
        # Configure the mock instance that will be returned when AsyncModbusTcpClient() is called.
        # This `mock_client_instance` represents the actual client object created by your component.
        mock_instance = MockModbusClient.return_value

        mock_connected_property = Mock(return_value=False)
        type(mock_instance).connected = property(lambda self: mock_connected_property())

        # When `connect` is called, it should change the `connected` property to True,
        # and return True which will be the return value of connect()
        async def connect_side_effect():
            mock_connected_property.return_value = True
            return True
        mock_instance.connect = AsyncMock(side_effect=connect_side_effect)

        # Mock the `read_holding_registers` method.
        mock_results_queue = []
        for registers_for_this_call in request.param:
            mock_read_holding_registers_result = AsyncMock()
            mock_read_holding_registers_result.registers = registers_for_this_call
            mock_read_holding_registers_result.isError = Mock(return_value=False)
            mock_read_holding_registers_result.exception_code = 0
            mock_results_queue.append(mock_read_holding_registers_result)
        mock_instance.read_holding_registers = AsyncMock(side_effect = mock_results_queue)

        # When `close` is called, it should change the `connected` property back to False.
        def close_side_effect():
            mock_connected_property.return_value = False
        # Mock the `close` method, as it might be called during component teardown or error handling.
        mock_instance.close = Mock(side_effect=close_side_effect)

        yield mock_instance

@pytest.mark.parametrize(
    "mock_modbus_tcp_client", # This refers to the fixture
    [
        ([
            list(range(1, len(MODBUS_SENSORS_GENERAL_STATE.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_HEATING_CURVE_1.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_COOLING_CURVE_1.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_HEATING_CURVE_2.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_COOLING_CURVE_2.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_HOT_WATER.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_NETWORK.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_HEATING_STATE.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_HEATING_CONTROL.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_HYDRAULIC_CIRCUIT.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_TEMPERATURES.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_PERFORMANCE.descriptors) + 1)),
            list(range(1, len(MODBUS_SENSORS_POWER.descriptors) + 1)),        ]),
        # ([...]),x
        # ([...]),
    ],
    indirect=True # This tells pytest to pass the parameter to the fixture
)

@pytest.mark.asyncio
async def test_async_setup_entry_modbus_ok(hass, mock_modbus_tcp_client):
    """Verify config entries for Modbus/TCP work."""

    global _mock_registers

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_MODBUSTCP,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
            CONF_HOST: MOCK_MODBUS_HOST,
            CONF_PORT: MOCK_MODBUS_PORT,
            CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
        },
        entry_id="test_entry_xtherma",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Verify setup worked
    _verify_entry(entry)

    # Verify sensors are initialized
    _verify_sensors(hass, entry)

