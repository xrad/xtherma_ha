"""Tests for the Xtherma API."""

import homeassistant.helpers.entity_registry as er
import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
)

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    EXTRA_STATE_ATTRIBUTE_PARAMETER,
    FERNPORTAL_URL,
)
from custom_components.xtherma_fp.xtherma_data import XthermaData
from tests.const import MOCK_API_KEY, MOCK_SERIAL_NUMBER
from tests.helpers import get_platform, load_mock_data


async def test_restapi_setup_entry_old(hass, aioclient_mock):
    """Verify old config entries without CONF_CONNECTION work."""
    mock_data = load_mock_data("rest_response.json")
    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    aioclient_mock.get(url, json=mock_data)

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: MOCK_API_KEY,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
        entry_id="test_entry_xtherma",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Verify setup worked
    verify_integration_entry(entry)


def verify_integration_entry(entry: ConfigEntry):
    assert isinstance(entry.runtime_data, XthermaData)
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.sensors_initialized


def verify_integration_sensors(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.sensors_initialized

    our_sensors = [
        state
        for state in hass.states.async_all(Platform.SENSOR)
        if state.entity_id.startswith(f"sensor.{entry.title}")
    ]
    if entry.data[CONF_CONNECTION] == CONF_CONNECTION_RESTAPI:
        assert len(our_sensors) == 54
    else:
        assert len(our_sensors) == 56


def verify_integration_switches(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.switches_initialized

    our_switches = [
        state
        for state in hass.states.async_all(Platform.SWITCH)
        if state.entity_id.startswith(f"switch.{entry.title}")
    ]
    assert len(our_switches) == 7


def verify_integration_numbers(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.numbers_initialized

    our_numbers = [
        state
        for state in hass.states.async_all(Platform.NUMBER)
        if state.entity_id.startswith(f"number.{entry.title}")
    ]
    assert len(our_numbers) == 25


def verify_integration_selects(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.selects_initialized

    our_selects = [
        state
        for state in hass.states.async_all(Platform.SELECT)
        if state.entity_id.startswith(f"select.{entry.title}")
    ]
    assert len(our_selects) == 2


def verify_parameter_keys(hass: HomeAssistant, entry: ConfigEntry):
    entity_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(entity_reg, entry.entry_id)
    for reg_entity in entries:
        domain = reg_entity.entity_id.split(".")[0]
        platform = get_platform(hass, domain)
        entity = platform.entities.get(reg_entity.entity_id)
        assert entity is not None
        assert entity.extra_state_attributes is not None
        key = entity.extra_state_attributes[EXTRA_STATE_ATTRIBUTE_PARAMETER]
        assert key == entity.entity_description.key


async def test_restapi_setup_entry_ok(hass, init_integration):
    """Verify config entries for REST API work."""
    entry = init_integration

    verify_integration_entry(entry)

    verify_integration_sensors(hass, entry)

    verify_integration_switches(hass, entry)

    verify_integration_numbers(hass, entry)

    verify_integration_selects(hass, entry)

    verify_parameter_keys(hass, entry)


@pytest.mark.parametrize("init_integration", [{"http_error": 429}], indirect=True)
async def test_restapi_setup_entry_read_busy(hass, aioclient_mock, init_integration):
    """Test busy restapi during setup."""
    entry = init_integration
    assert entry.state.value == "setup_retry"
    assert entry.reason == "Read data too frequently"


@pytest.mark.parametrize("init_integration", [{"http_error": 404}], indirect=True)
async def test_restapi_setup_entry_404(hass, aioclient_mock, init_integration):
    """Test busy restapi during setup."""
    entry = init_integration
    assert entry.state.value == "setup_retry"
    assert entry.reason == "REST-API error 404"


@pytest.mark.parametrize("init_integration", [{"timeout_error": True}], indirect=True)
async def test_restapi_setup_entry_timeout(hass, aioclient_mock, init_integration):
    """Test busy restapi during setup."""
    entry = init_integration
    assert entry.state.value == "setup_retry"
    assert entry.reason == "Timeout error"
