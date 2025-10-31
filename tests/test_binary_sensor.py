"""Tests for the Xtherma sensor platform."""

from unittest.mock import patch

import pytest
from homeassistant.const import Platform
from pytest_homeassistant_custom_component.common import snapshot_platform

from tests.conftest import init_integration, init_modbus_integration
from tests.helpers import (
    get_binary_sensor_platform,
    provide_modbus_data,
    provide_rest_data,
)

BINARY_SENSOR_ENTITY_ID_PK = (
    "binary_sensor.test_entry_xtherma_config_pk_circulation_pump_enabled"
)
BINARY_SENSOR_ENTITY_ID_PWW = (
    "binary_sensor.test_entry_xtherma_config_pww_circulation_pump_hot_water_enabled"
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


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_binary_sensor_state(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)
    pk = hass.states.get(BINARY_SENSOR_ENTITY_ID_PK)
    assert pk.state == "off"
    pww = hass.states.get(BINARY_SENSOR_ENTITY_ID_PWW)
    assert pww.state == "on"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_binary_sensor_icon(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)
    platform = get_binary_sensor_platform(hass)
    pk = hass.states.get(BINARY_SENSOR_ENTITY_ID_PK)
    assert pk.state == "off"
    e_pk = platform.entities.get(pk.entity_id)
    assert e_pk is not None
    assert e_pk.icon == "mdi:pump-off"
    pww = hass.states.get(BINARY_SENSOR_ENTITY_ID_PWW)
    assert pww.state == "on"
    e_pww = platform.entities.get(pww.entity_id)
    assert e_pww is not None
    assert e_pww.icon == "mdi:pump"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_binary_sensor_name(hass, mock_rest_api_client):
    """Check if binary sensors have a proper (translated) names."""
    await init_integration(hass, mock_rest_api_client)
    platform = get_binary_sensor_platform(hass)
    state = hass.states.get(BINARY_SENSOR_ENTITY_ID_PWW)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.name == "[PWW] Circulation pump hot water enabled"
