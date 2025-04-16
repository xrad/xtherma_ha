import logging
from aiohttp import ClientResponseError, RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_API_KEY

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xtherma_fp.const import CONF_CONNECTION, CONF_CONNECTION_RESTAPI, CONF_SERIAL_NUMBER, DOMAIN, FERNPORTAL_URL
from pytest_homeassistant_custom_component.common import load_json_value_fixture

from custom_components.xtherma_fp.xtherma_data import XthermaData
from tests.const import MOCK_API_KEY, MOCK_SERIAL_NUMBER
from yarl import URL


@pytest.mark.asyncio
async def test_async_setup_entry_old(hass, aioclient_mock):
    """Verify old config entries without CONF_CONNECTION work."""
    mock_data = load_json_value_fixture("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
    )

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
    assert entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_setup_entry_restapi(hass, aioclient_mock):
    """Verify config entries for REST API work."""
    mock_data = load_json_value_fixture("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
    )

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
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
    assert entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]
    assert type(hass.data[DOMAIN][entry.entry_id]) is XthermaData
    xtherma_data: XthermaData = hass.data[DOMAIN][entry.entry_id]
    assert xtherma_data.sensors_initialized

@pytest.mark.asyncio
async def test_async_setup_entry_restapi_delay(hass, aioclient_mock, caplog):
    """Verify config entries for REST API work."""

    print("Test ----------------")
    logger_name = f"custom_components.{DOMAIN}"
    caplog.set_level(logging.DEBUG, logger=logger_name)

    def make_response_error(url: str, status: int):
        return ClientResponseError(
            request_info=RequestInfo(
                url=URL(url),
                method="GET",
                headers=CIMultiDictProxy(CIMultiDict()),
                real_url=URL(url),
            ),
            history=(),
            status=status,
            message=f"Simulated error {status}",
        )
    mock_data = load_json_value_fixture("rest_response.json")
    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    aioclient_mock.get(
        url,
        side_effect=[
            mock_data,
            make_response_error(url, 429)
        ],
    )

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
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
    assert entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]
    assert type(hass.data[DOMAIN][entry.entry_id]) is XthermaData
    xtherma_data: XthermaData = hass.data[DOMAIN][entry.entry_id]
    assert not xtherma_data.sensors_initialized
