"""Test config flow."""

import pytest
from homeassistant.data_entry_flow import FlowResultType
from custom_components.xtherma_fp.const import (
    CONF_SERIAL_NUMBER,
)
from homeassistant.const import CONF_API_KEY

from tests.const import MOCK_API_KEY, MOCK_SERIAL_NUMBER
from homeassistant.config_entries import (
    ConfigEntryState,
)


@pytest.mark.asyncio
async def test_options_flow_rest_api_ok(hass, init_integration):
    """Test giving an valid data to REST API config flow."""

    entry = init_integration
    assert entry.state is ConfigEntryState.LOADED

    result = await hass.config_entries.options.async_init(
        entry.entry_id,
        context={"source": "test"}, data=None
        )
    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY, CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
