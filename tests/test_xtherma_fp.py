"""Tests for the Xtherma API."""

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_API_KEY
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
)

from custom_components.xtherma_fp.const import (
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
)
from tests.const import MOCK_API_KEY, MOCK_SERIAL_NUMBER
from tests.helpers import load_mock_data, provide_rest_data

from .conftest import init_integration


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

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state is ConfigEntryState.LOADED


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_restapi_setup_entry_ok(hass, mock_rest_api_client):
    """Verify config entries for REST API work."""
    entry = await init_integration(hass, mock_rest_api_client)

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state is ConfigEntryState.LOADED


@pytest.mark.parametrize(
    "mock_rest_api_client", provide_rest_data(http_error=429), indirect=True
)
async def test_restapi_setup_entry_read_busy(hass, mock_rest_api_client):
    """Test busy restapi during setup."""
    entry = await init_integration(hass, mock_rest_api_client)
    assert entry.state.value == "setup_retry"
    assert entry.reason == "Read data too frequently"


@pytest.mark.parametrize(
    "mock_rest_api_client", provide_rest_data(http_error=404), indirect=True
)
async def test_restapi_setup_entry_404(hass, mock_rest_api_client):
    """Test busy restapi during setup."""
    entry = await init_integration(hass, mock_rest_api_client)
    assert entry.state.value == "setup_retry"
    assert entry.reason == "REST-API error 404"


@pytest.mark.parametrize(
    "mock_rest_api_client", provide_rest_data(timeout_error=True), indirect=True
)
async def test_restapi_setup_entry_timeout(hass, mock_rest_api_client):
    """Test busy restapi during setup."""
    entry = await init_integration(hass, mock_rest_api_client)
    assert entry.state.value == "setup_retry"
    assert entry.reason == "Timeout error"
