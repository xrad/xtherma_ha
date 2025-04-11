import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_API_KEY

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xtherma_fp.const import CONF_CONNECTION, CONF_CONNECTION_RESTAPI, CONF_SERIAL_NUMBER, DOMAIN, FERNPORTAL_URL
from pytest_homeassistant_custom_component.common import load_json_value_fixture

from tests.const import MOCK_API_KEY, MOCK_SERIAL_NUMBER


@pytest.mark.asyncio
async def test_async_setup_entry(hass, aioclient_mock):

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
