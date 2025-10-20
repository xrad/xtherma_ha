"""Helpers for tests."""

from typing import Any

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


def find_entry(values: list[dict], key: str) -> dict[str, Any] | None:
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


def load_modbus_regs_from_json(filename: str) -> list[dict[str, Any]]:
    """Read and return a complete Modbus register read-out from Json.

    The Json file can be directly based on the REST-API response.
    Beware of keys which are not not defined in the REST-API but
    exist for Modbus.

    Each register "bank" will be read with its own call to read_holding_registers
    so there is also to option to inject an exception code for the read.

    Returns:
        [
            # Modbus registers 0..2
            { "registers": [reg 0, reg 1, reg 2],
              "exc_code": None
            },
            # Modbus registers 10..15
            { "registers": [reg 10, reg 11, reg 12, ...],
              "exc_code": None
            }
            ...
        ]
    """
    # Create a mock config entry
    mock_data = load_mock_data(filename)
    assert isinstance(mock_data, dict)
    telemetry = mock_data[KEY_TELEMETRY]
    settings = mock_data[KEY_SETTINGS]
    assert isinstance(telemetry, list)
    assert isinstance(settings, list)
    all_values = telemetry
    all_values.extend(settings)
    regs_list: list[dict[str, Any]] = []
    for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
        regs = [0] * len(reg_desc.descriptors)
        for i, desc in enumerate(reg_desc.descriptors):
            if desc is None:
                continue
            entry = find_entry(all_values, desc.key)
            if entry is None:
                continue
            value = int(str(entry[KEY_ENTRY_VALUE]))
            regs[i] = value
        regs_list.append(
            {
                "registers": regs,
                "exc_code": None,
            }
        )
    return regs_list


def load_rest_response() -> list[list[dict[str, Any]]]:
    """Return a list of complete Modbus register read-outs.

    Currently returns only one read-out based on our standard REST API response.
    """
    regs_list = load_modbus_regs_from_json("rest_response.json")
    return [regs_list]
