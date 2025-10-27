"""Tests for the Xtherma Modbus API."""

from typing import TYPE_CHECKING

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers.update_coordinator import UpdateFailed
from pymodbus.pdu.pdu import ExceptionResponse

from custom_components.xtherma_fp.const import DOMAIN
from tests.conftest import MockModbusParam
from tests.helpers import (
    get_sensor_platform,
    provide_modbus_data,
)
from tests.test_xtherma_fp import (
    verify_integration_binary_sensors,
    verify_integration_numbers,
    verify_integration_selects,
    verify_integration_sensors,
    verify_integration_switches,
    verify_parameter_keys,
)

if TYPE_CHECKING:
    from custom_components.xtherma_fp import XthermaData

SENSOR_ENTITY_ID_MODE = "sensor.test_entry_xtherma_modbus_config_current_operating_mode"


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",
    provide_modbus_data(),
    indirect=True,
)
@pytest.mark.asyncio
async def test_async_setup_entry_modbus_ok(hass, init_modbus_integration):
    # Verify setup worked
    entry = init_modbus_integration

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state is ConfigEntryState.LOADED

    verify_integration_binary_sensors(hass, entry)

    verify_integration_sensors(hass, entry)

    verify_integration_switches(hass, entry)

    verify_integration_numbers(hass, entry)

    verify_integration_selects(hass, entry)

    verify_parameter_keys(hass, entry)


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",
    provide_modbus_data(exc_code=ExceptionResponse.SLAVE_BUSY),
    indirect=True,
)
@pytest.mark.asyncio
async def test_modbus_setup_entry_read_busy(hass, init_modbus_integration):
    """Test busy modbus during setup."""
    entry = init_modbus_integration
    assert entry.state.value == "setup_retry"
    assert entry.reason == "Modbus interface is busy"


def _test_modbus_runtime_read_busy() -> list[MockModbusParam]:
    # prepare register set for 2 update cyles:
    # 1. ok (for config entry setup)
    # 2. busy (for first regular update)
    param_setup: list[MockModbusParam] = provide_modbus_data()
    param_runtime: list[MockModbusParam] = provide_modbus_data()
    for regs in param_runtime[0]:
        regs["exc_code"] = ExceptionResponse.SLAVE_BUSY
    return [param_setup[0] + param_runtime[0]]


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",
    _test_modbus_runtime_read_busy(),
    indirect=True,
)
@pytest.mark.asyncio
async def test_modbus_runtime_read_busy(hass, init_modbus_integration, caplog):
    """Test busy modbus at runtime setup."""
    caplog.set_level("ERROR")

    entry = init_modbus_integration
    assert entry.state.value == "loaded"

    # get coordinator and verify last update was ok
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data is not None
    assert xtherma_data.coordinator is not None
    coordinator = xtherma_data.coordinator
    assert coordinator.last_update_success

    platform = get_sensor_platform(hass)
    state = hass.states.get(SENSOR_ENTITY_ID_MODE)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.state == "water"
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data is not None
    assert xtherma_data.coordinator is not None
    await xtherma_data.coordinator.async_request_refresh()

    # check last update was not ok
    assert not coordinator.last_update_success
    assert isinstance(coordinator.last_exception, UpdateFailed)
    assert coordinator.last_exception.translation_key == "modbus_read_busy_error"
    # verify that last state is still valid
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.state == "water"

    assert any(
        rec.levelname == "ERROR"
        and "Modbus interface is busy" in rec.message
        and "custom_components." + DOMAIN in rec.name
        for rec in caplog.records
    )
