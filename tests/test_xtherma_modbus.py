"""Tests for the Xtherma Modbus API."""

from typing import Any

import pytest
from pymodbus.pdu.pdu import ExceptionResponse

from tests.helpers import (
    load_modbus_regs_from_json,
    load_rest_response,
)
from tests.test_xtherma_fp import (
    verify_integration_entry,
    verify_integration_numbers,
    verify_integration_selects,
    verify_integration_sensors,
    verify_integration_switches,
    verify_parameter_keys,
)


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    load_rest_response(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
@pytest.mark.asyncio
async def test_async_setup_entry_modbus_ok(hass, init_modbus_integration):
    # Verify setup worked
    entry = init_modbus_integration
    assert entry.state.value == "loaded"

    verify_integration_entry(entry)

    verify_integration_sensors(hass, entry)

    verify_integration_switches(hass, entry)

    verify_integration_numbers(hass, entry)

    verify_integration_selects(hass, entry)

    verify_parameter_keys(hass, entry)


def _test_modbus_setup_entry_read_busy_regs() -> list[list[dict[str, Any]]]:
    regs_list = load_modbus_regs_from_json("rest_response.json")
    for regs in regs_list:
        regs["exc_code"] = ExceptionResponse.SLAVE_BUSY
    return [regs_list]


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    _test_modbus_setup_entry_read_busy_regs(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
@pytest.mark.asyncio
async def test_modbus_setup_entry_read_busy(hass, init_modbus_integration):
    """Test busy modbus during setup."""
    entry = init_modbus_integration
    assert entry.state.value == "setup_retry"
    assert entry.reason == "Modbus interface is busy"
