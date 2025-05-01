"""Test config flow."""

import asyncio
import pytest
from homeassistant.data_entry_flow import FlowResultType
from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    FERNPORTAL_URL,
)
from homeassistant.const import CONF_API_KEY
from pytest_homeassistant_custom_component.common import load_json_value_fixture

from tests.const import MOCK_API_KEY, MOCK_SERIAL_NUMBER


async def test_rest_api_bad_arguments(hass):
    """Test giving bad config dat to REST API config flow."""

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp", context={"source": "user"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_CONNECTION: CONF_CONNECTION_RESTAPI}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_API_KEY: MOCK_API_KEY,
            CONF_SERIAL_NUMBER: "SerialNumbersMustBeginWithFP",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    assert result["errors"] == {"base": "bad_arguments"}


async def test_rest_api_good_serial_number(hass, aioclient_mock):
    """Test giving an valid data to REST API config flow."""

    mock_data = load_json_value_fixture("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp", context={"source": "user"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_CONNECTION: CONF_CONNECTION_RESTAPI}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY, CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_rest_error_404(hass, aioclient_mock):
    """Test forcing network errors to REST API config flow."""

    mock_data = load_json_value_fixture("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
        status=404,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp", context={"source": "user"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_CONNECTION: CONF_CONNECTION_RESTAPI}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY, CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    assert result["errors"] == {"base": "unknown"}


async def test_rest_error_429(hass, aioclient_mock):
    """Test forcing network errors to REST API config flow."""

    mock_data = load_json_value_fixture("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
        status=429,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp", context={"source": "user"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_CONNECTION: CONF_CONNECTION_RESTAPI}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY, CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    assert result["errors"] == {"base": "rate_limit"}


async def test_rest_error_timeout(hass, aioclient_mock):
    """Test forcing network errors to REST API config flow."""

    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}", exc=asyncio.exceptions.TimeoutError
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp", context={"source": "user"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_CONNECTION: CONF_CONNECTION_RESTAPI}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY, CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    assert result["errors"] == {"base": "timeout"}
