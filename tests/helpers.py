from typing import Any
import warnings
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, State
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import async_get_platforms, EntityPlatform
from homeassistant.util.json import (
    JsonValueType,
)
from pytest import fail

from custom_components.xtherma_fp.const import DOMAIN, KEY_ENTRY_KEY, KEY_ENTRY_VALUE, KEY_SETTINGS, KEY_TELEMETRY
from pytest_homeassistant_custom_component.common import (
    load_json_value_fixture,
)

from custom_components.xtherma_fp.entity_descriptors import MODBUS_ENTITY_DESCRIPTIONS

def find_sensor_state(hass: HomeAssistant, entry: ConfigEntry, id: str) -> State:
    full_id = f"sensor.{entry.entry_id}_{id}"
    state = hass.states.get(full_id)
    assert state is not None
    return state


def find_switch_state(hass: HomeAssistant, entry: ConfigEntry, id: str) -> State:
    full_id = f"switch.{entry.entry_id}_{id}"
    state = hass.states.get(full_id)
    assert state is not None
    return state


def find_number_state(hass: HomeAssistant, entry: ConfigEntry, id: str) -> State:
    full_id = f"number.{entry.entry_id}_{id}"
    state = hass.states.get(full_id)
    assert state is not None
    return state


def find_select_state(hass: HomeAssistant, entry: ConfigEntry, id: str) -> State:
    full_id = f"select.{entry.entry_id}_{id}"
    state = hass.states.get(full_id)
    assert state is not None
    return state


def get_sensor_platform(hass: HomeAssistant) -> EntityPlatform:
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 4
    for platform in platforms:
        if platform.domain == Platform.SENSOR:
            return platform
    fail("We have no sensor platfom")

def get_switch_platform(hass: HomeAssistant) -> EntityPlatform:
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 4
    for platform in platforms:
        if platform.domain == Platform.SWITCH:
            return platform
    fail("We have no switch platfom")


def get_number_platform(hass: HomeAssistant) -> EntityPlatform:
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 4
    for platform in platforms:
        if platform.domain == Platform.NUMBER:
            return platform
    fail("We have no number platfom")


def get_select_platform(hass: HomeAssistant) -> EntityPlatform:
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 4
    for platform in platforms:
        if platform.domain == Platform.SELECT:
            return platform
    fail("We have no select platfom")


def find_entry(values: list[dict], key: str) -> dict[str, Any] | None:
    for entry in values:
        if entry[KEY_ENTRY_KEY] == key:
            return entry
    raise Exception(f"Key {key} not found")

def load_mock_data(filename: str) -> JsonValueType:
    mock_data = load_json_value_fixture(filename)
    return mock_data


def load_modbus_regs_from_json(filename: str) -> list[list[int]]:
    """Integration using Modbus."""
    # Create a mock config entry
    mock_data = load_mock_data(filename)
    assert(isinstance(mock_data, dict))
    telemetry = mock_data[KEY_TELEMETRY]
    settings = mock_data[KEY_SETTINGS]
    assert(isinstance(telemetry, list))
    assert(isinstance(settings, list))
    all_values = telemetry
    all_values.extend(settings)
    regs_list = []
    for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
        regs = [0] * len(reg_desc.descriptors)
        for i, desc in enumerate(reg_desc.descriptors):
            if desc is None:
                continue
            entry = find_entry(all_values, desc.key) # type: ignore
            if entry is None:
                continue
            value = int(str(entry[KEY_ENTRY_VALUE]))
            # print(f"{desc.key} {reg_desc.base}+{i} {reg_desc.base+i} = {value}")
            regs[i] = value
        regs_list.append(regs)
    return regs_list

def load_rest_response():
    regs_list = load_modbus_regs_from_json("rest_response.json")
    return [
        regs_list
        # ([...]),x
        # ([...]),
    ]
