"""Set up some common test helper things."""

import asyncio
from typing import cast
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import CONF_ADDRESS, CONF_API_KEY, CONF_HOST, CONF_PORT
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
)

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
    VERSION,
)
from tests.const import (
    MOCK_API_KEY,
    MOCK_CONFIG_ENTRY_ID,
    MOCK_MODBUS_ADDRESS,
    MOCK_MODBUS_HOST,
    MOCK_MODBUS_PORT,
    MOCK_SERIAL_NUMBER,
)
from tests.helpers import load_mock_data


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    return


@pytest.fixture
async def init_integration(
    hass, aioclient_mock, request: pytest.FixtureRequest
) -> MockConfigEntry:
    """Integration using REST API."""
    param = getattr(request, "param", None)
    http_error = None
    timeout_error = None
    if param is not None:
        http_error = param.get("http_error")
        timeout_error = param.get("timeout_error")

    mock_data = load_mock_data("rest_response.json")
    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    if http_error is not None:
        aioclient_mock.get(url, status=http_error)
    elif timeout_error is not None:

        def raise_timeout(*args, **kwargs):
            raise asyncio.exceptions.TimeoutError

        aioclient_mock.get(url, side_effect=raise_timeout)
    else:
        aioclient_mock.get(url, json=mock_data)

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_API_KEY: MOCK_API_KEY,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
        entry_id=MOCK_CONFIG_ENTRY_ID,
        version=VERSION,
        title="test_entry_xtherma_config",
        source="user",
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry


MODBUS_CLIENT_PATH = (
    "custom_components.xtherma_fp.xtherma_client_modbus.AsyncModbusTcpClient"
)


@pytest.fixture
async def mock_modbus_tcp_client(request: pytest.FixtureRequest):
    """Stub out Modbus calls."""
    with patch(MODBUS_CLIENT_PATH) as mock_modbus_client:
        # Configure the mock instance that will be returned when AsyncModbusTcpClient() is called.
        # This `mock_client_instance` represents the actual client object created by your component.
        mock_instance = mock_modbus_client.return_value

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
        assert isinstance(request.param, list)
        for registers_for_this_call in request.param:
            assert isinstance(registers_for_this_call, dict)
            reg_list = registers_for_this_call.get("registers")
            assert registers_for_this_call is not None
            exc_code = registers_for_this_call.get("exc_code")
            mock_read_holding_registers_result = AsyncMock()
            mock_read_holding_registers_result.registers = reg_list
            if exc_code is not None:
                mock_read_holding_registers_result.isError = Mock(return_value=True)
                mock_read_holding_registers_result.exception_code = exc_code
            else:
                mock_read_holding_registers_result.isError = Mock(return_value=False)
                mock_read_holding_registers_result.exception_code = 0
            mock_results_queue.append(mock_read_holding_registers_result)
        mock_instance.read_holding_registers = AsyncMock(side_effect=mock_results_queue)

        # When `close` is called, it should change the `connected` property back to False.
        def close_side_effect():
            mock_connected_property.return_value = False

        # Mock the `write_registers` method
        mock_write_register_result = AsyncMock()
        mock_write_register_result.isError = Mock(return_value=False)
        mock_write_register_result.exception_code = 0
        mock_instance.write_register = AsyncMock(
            return_value=mock_write_register_result
        )

        # Mock the `close` method, as it might be called during component teardown or error handling.
        mock_instance.close = Mock(side_effect=close_side_effect)

        yield mock_instance


@pytest.fixture
async def init_modbus_integration(hass, mock_modbus_tcp_client) -> MockConfigEntry:
    """Integration using Modbus."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_MODBUSTCP,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
            CONF_HOST: MOCK_MODBUS_HOST,
            CONF_PORT: MOCK_MODBUS_PORT,
            CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
        },
        entry_id=MOCK_CONFIG_ENTRY_ID,
        version=VERSION,
        title="test_entry_xtherma_modbus_config",
        source="user",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry
