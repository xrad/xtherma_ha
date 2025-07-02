from unittest.mock import Mock, patch
import pytest
from unittest.mock import AsyncMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_HOST, CONF_PORT

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_SERIAL_NUMBER,
    DOMAIN,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from custom_components.xtherma_fp.xtherma_data import XthermaData
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from tests.const import MOCK_MODBUS_ADDRESS, MOCK_MODBUS_HOST, MOCK_MODBUS_PORT, MOCK_SERIAL_NUMBER


def _verify_entry(entry: ConfigEntry):
    assert isinstance(entry.runtime_data, XthermaData)


def _verify_sensors(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.sensors_initialized

    our_sensors = [
        state
        for state in hass.states.async_all("sensor")
        if state.entity_id.startswith("sensor.xtherma_fp")
    ]
    assert len(our_sensors) == 6

    # check first sensor state
    state = our_sensors[0]
    assert state.state == "0.1"
    assert state.entity_id == "sensor.xtherma_fp_tw"
    assert state.attributes["device_class"] == SensorDeviceClass.TEMPERATURE
    assert state.attributes["unit_of_measurement"] == "°C"

    # check last sensor state
    state = our_sensors[len(our_sensors) - 1]
    assert state.entity_id == "sensor.xtherma_fp_tk2"
    assert state.state == "6454.6"
    assert state.attributes["device_class"] == SensorDeviceClass.TEMPERATURE
    assert state.attributes["unit_of_measurement"] == "°C"

from pymodbus.client import AsyncModbusTcpClient

MODBUS_CLIENT_PATH = "custom_components.xtherma_fp.xtherma_client_modbus.AsyncModbusTcpClient"

@pytest.fixture
async def mock_modbus_tcp_client(request):
    mock_registers = getattr(request, "param", [])
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
        # This method typically returns a response object that has a 'registers' attribute.
        # Create an AsyncMock for the method itself.
        mock_read_holding_registers_result = AsyncMock()
        # Set the 'registers' attribute on the *result* of the read_holding_registers call.
        # These are the dummy values your Modbus client code will "read".
        mock_read_holding_registers_result.registers = mock_registers
        mock_read_holding_registers_result.isError = Mock(return_value=False)
        mock_read_holding_registers_result.exception_code = 0

        # Assign the configured AsyncMock to the read_holding_registers method of the client instance.
        mock_instance.read_holding_registers = AsyncMock(
            return_value=mock_read_holding_registers_result
        )

        # When `close` is called, it should change the `connected` property back to False.
        def close_side_effect():
            mock_connected_property.return_value = False
        # Mock the `close` method, as it might be called during component teardown or error handling.
        mock_instance.close = Mock(side_effect=close_side_effect)

        yield mock_instance

def dummy():
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
        # This method typically returns a response object that has a 'registers' attribute.
        # Create an AsyncMock for the method itself.
        mock_read_holding_registers_result = AsyncMock()
        # Set the 'registers' attribute on the *result* of the read_holding_registers call.
        # These are the dummy values your Modbus client code will "read".
        mock_read_holding_registers_result.registers = [1, 4, 344, 361, 276, 260, 64546, 180, 350, 1] # Example register values
        mock_read_holding_registers_result.isError = Mock(return_value=False)
        mock_read_holding_registers_result.exception_code = 0

        # Assign the configured AsyncMock to the read_holding_registers method of the client instance.
        mock_instance.read_holding_registers = AsyncMock(
            return_value=mock_read_holding_registers_result
        )

        # When `close` is called, it should change the `connected` property back to False.
        async def close_side_effect():
            mock_connected_property.return_value = False
        # Mock the `close` method, as it might be called during component teardown or error handling.
        mock_instance.close = AsyncMock(side_effect=close_side_effect)

@pytest.mark.parametrize(
    "mock_modbus_tcp_client", # This refers to the fixture
    [
        ([1, 4, 344, 361, 276, 260, 64546, 180, 350, 1]),
        # ([...]),
        # ([...]),
    ],
    indirect=True # This tells pytest to pass the parameter to the fixture
)

@pytest.mark.asyncio
async def test_async_setup_entry_modbus_ok(hass, mock_modbus_tcp_client):
    """Verify config entries for Modbus/TCP work."""

    global _mock_registers

    # _mock_registers = [1, 4, 344, 361, 276, 260, 64546, 180, 350, 1]

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

