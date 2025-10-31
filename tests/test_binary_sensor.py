"""Tests for the Xtherma sensor platform."""

from unittest.mock import patch

import pytest
from homeassistant.const import Platform
from pytest_homeassistant_custom_component.common import snapshot_platform

from tests.conftest import init_integration, init_modbus_integration
from tests.helpers import (
    provide_modbus_data,
    provide_rest_data,
)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_setup_binary_sensor_rest_api(
    hass, entity_registry, snapshot, mock_rest_api_client
) -> None:
    """Test the setup of binary sensor platform using REST API."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.BINARY_SENSOR]):
        entry = await init_integration(hass, mock_rest_api_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_setup_binary_sensor_modbus_tcp(
    hass, entity_registry, snapshot, mock_modbus_tcp_client
) -> None:
    """Test the setup of binary sensor platform using MODBUS TCP."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.BINARY_SENSOR]):
        entry = await init_modbus_integration(hass, mock_modbus_tcp_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)
