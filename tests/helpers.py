"""Helpers for tests."""

from typing import Any, cast

import pytest
from homeassistant.const import Platform
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
from custom_components.xtherma_fp.entity_descriptors import MODBUS_ENTITY_DESCRIPTIONS
from tests.conftest import (
    MockModbusParam,
    MockModbusParamExceptionCode,
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


def get_sensor_platform(hass: HomeAssistant) -> EntityPlatform:
    return get_platform(hass, Platform.SENSOR)


def get_switch_platform(hass: HomeAssistant) -> EntityPlatform:
    return get_platform(hass, Platform.SWITCH)


def get_number_platform(hass: HomeAssistant) -> EntityPlatform:
    return get_platform(hass, Platform.NUMBER)


def get_select_platform(hass: HomeAssistant) -> EntityPlatform:
    return get_platform(hass, Platform.SELECT)


def find_entry(values: list[dict], key: str) -> dict[str, Any]:
    for entry in values:
        if entry[KEY_ENTRY_KEY] == key:
            return entry
    raise KeyError(key)


def load_mock_data(filename: str) -> JsonValueType:
    mock_data = load_json_value_fixture(filename)
    assert isinstance(mock_data, dict)
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


def _flatten_mock_data(mock_data: JsonValueType) -> list[dict[str, Any]]:
    mock_data = cast("dict[str, Any]", mock_data)
    telemetry = cast("list[dict[str, int|str]]", mock_data[KEY_TELEMETRY])
    settings = cast("list[dict[str, int|str]]", mock_data[KEY_SETTINGS])
    all_values = telemetry
    all_values.extend(settings)
    return all_values


def _load_modbus_data_from_json(
    filename: str, exc_code: MockModbusParamExceptionCode = None
) -> MockModbusParam:
    mock_data = load_mock_data(filename)
    all_values = _flatten_mock_data(mock_data)
    regs_list: MockModbusParam = []
    for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
        regs = [0] * len(reg_desc.descriptors)
        for i, desc in enumerate(reg_desc.descriptors):
            if desc is None:
                continue
            entry = find_entry(all_values, desc.key)
            value = int(str(entry[KEY_ENTRY_VALUE]))
            regs[i] = value
        regs_list.append(
            {
                "registers": regs,
                "exc_code": exc_code,
            }
        )
    return regs_list


def provide_modbus_data(
    exc_code: MockModbusParamExceptionCode = None,
) -> list[MockModbusParam]:
    """Return a list of complete Modbus register read-outs.

    Currently returns only one read-out based on our standard REST API response.
    """
    regs_list = _load_modbus_data_from_json("rest_response.json", exc_code=exc_code)
    return [regs_list]
