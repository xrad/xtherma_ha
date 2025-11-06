"""Helpers for tests."""

from typing import Any, cast

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import EntityPlatform, async_get_platforms
from homeassistant.util.json import (
    JsonValueType,
)
from pytest_homeassistant_custom_component.common import (
    load_json_value_fixture,
)

from custom_components.xtherma_fp.const import (
    DOMAIN,
    KEY_ENTRY_INPUT_FACTOR,
    KEY_ENTRY_KEY,
    KEY_ENTRY_VALUE,
    KEY_SETTINGS,
    KEY_TELEMETRY,
)
from custom_components.xtherma_fp.entity_descriptors import (
    MODBUS_ENTITY_DESCRIPTIONS,
    MODBUS_REGISTER_RANGES,
    MODBUS_REGISTER_SIZE,
)
from tests.conftest import (
    MockModbusParam,
    MockModbusParamExceptionCode,
    MockModbusParamReadResult,
    MockModbusParamRegisters,
    MockRestParam,
    MockRestParamHttpError,
    MockRestParamTimeoutError,
)


def get_platform(hass: HomeAssistant, domain: str) -> EntityPlatform:
    platforms = async_get_platforms(hass, DOMAIN)
    for platform in platforms:
        if platform.domain == domain:
            return platform
    pytest.fail(f"We have no platfom {domain}")


def load_mock_data(filename: str) -> JsonValueType:
    """Load mock data from specified JSON file.

    The JSON file is expected to be an exact dump of the REST API response
    as documented on https://github.com/Xtherma/xtherma_api.

    The same mock data is used for REST API and Modbus/TCP tests where
    possible. However, the Modbus/TCP interface provides more data
    than what is received via REST, so we manually enrich the data
    read from file.
    """
    mock_data = load_json_value_fixture(filename)
    assert isinstance(mock_data, dict)
    # add registers only available via Modbus
    settings = mock_data[KEY_SETTINGS]
    assert isinstance(settings, list)
    settings.append(
        {
            KEY_ENTRY_KEY: "in_total",
            KEY_ENTRY_VALUE: "0",
            KEY_ENTRY_INPUT_FACTOR: "*10",
        },
    )
    settings.append(
        {
            KEY_ENTRY_KEY: "out_total",
            KEY_ENTRY_VALUE: "0",
            KEY_ENTRY_INPUT_FACTOR: "*10",
        },
    )
    return mock_data


def flatten_mock_data(mock_data: JsonValueType) -> list[dict[str, Any]]:
    """Merge telemetry and settings sections for easier access."""
    mock_data = cast("dict[str, Any]", mock_data)
    telemetry = cast("list[dict[str, int|str]]", mock_data[KEY_TELEMETRY])
    settings = cast("list[dict[str, int|str]]", mock_data[KEY_SETTINGS])
    flattened_mock_data = telemetry
    flattened_mock_data.extend(settings)
    return flattened_mock_data


def find_entry(flattened_mock_data: list[dict], key: str) -> dict[str, Any]:
    """Find entry by key in flattened mock data."""
    for entry in flattened_mock_data:
        if entry[KEY_ENTRY_KEY] == key:
            return entry
    pytest.fail(f"Unknown key {key}")


def provide_rest_data(
    http_error: MockRestParamHttpError = None,
    timeout_error: MockRestParamTimeoutError = None,
) -> list[MockRestParam]:
    """Load and return canned REST response.

    Currently returns only one REST API response.
    """
    response = load_mock_data("rest_response.json")
    result: MockRestParam = {
        "response": response,
        "http_error": http_error,
        "timeout_error": timeout_error,
    }
    return [result]


def get_modbus_register_number(key: str) -> int:
    for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
        for i, desc in enumerate(reg_desc.descriptors):
            if desc is None:
                continue
            if desc.key == key:
                return reg_desc.base + i
    pytest.fail(f"Unknown key {key}")


def set_modbus_register(param: MockModbusParam, key: str, value: int):
    regno = get_modbus_register_number(key)
    # find corresponding register range and modify value
    for i, r in enumerate(MODBUS_REGISTER_RANGES):
        if regno >= r.first_reg and regno <= r.last_reg:
            offset = regno - r.first_reg
            reg_list: MockModbusParamReadResult = param[i]
            regs = cast("MockModbusParamRegisters", reg_list["registers"])
            regs[offset] = value
            return
    # cannot happen, test_modbus_register_range_coverage verifies
    # all registers are covered by MODBUS_REGISTER_RANGES
    pytest.fail(f"Key {key} not found in range?!")


def provide_modbus_data(
    exc_code: MockModbusParamExceptionCode = None,
) -> list[MockModbusParam]:
    """Return a list of complete Modbus register read-outs.

    Currently returns only one read-out based on our standard REST API response.
    """
    param = provide_empty_modbus_data(exc_code=exc_code)
    regs_list = param[0]

    # get mock data from file and write it to the correct
    # register positions
    mock_data = load_mock_data("rest_response.json")
    all_values = flatten_mock_data(mock_data)
    for entry in all_values:
        key = entry[KEY_ENTRY_KEY]
        value = int(str(entry[KEY_ENTRY_VALUE]))
        set_modbus_register(regs_list, key, value)

    return param


def provide_empty_modbus_data(
    exc_code: MockModbusParamExceptionCode = None,
) -> list[MockModbusParam]:
    """Return a list of complete, but empty Modbus register read-outs."""
    # flat register map
    raw_registers = [0] * MODBUS_REGISTER_SIZE

    # prepare respsonses for read_holding_registers()
    regs_list: MockModbusParam = []
    for r in MODBUS_REGISTER_RANGES:
        regs_list.append(
            {
                "registers": raw_registers[r.first_reg : r.last_reg + 1],
                "exc_code": exc_code,
            }
        )

    return [regs_list]
