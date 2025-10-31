"""Tests for the Xtherma select platform."""

import pytest
from homeassistant.components.select import (
    SelectEntity,
)
from homeassistant.exceptions import HomeAssistantError

from custom_components.xtherma_fp.xtherma_client_common import XthermaReadOnlyError
from tests.helpers import (
    get_select_platform,
    provide_modbus_data,
    provide_rest_data,
)

from .conftest import init_integration, init_modbus_integration

SELECT_ENTITY_ID_002 = "select.test_entry_xtherma_config_operating_mode"
SELECT_ENTITY_ID_MODBUS_002 = "select.test_entry_xtherma_modbus_config_operating_mode"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_select_entity(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)
    platform = get_select_platform(hass)
    state = hass.states.get(SELECT_ENTITY_ID_002)
    assert state.state == "auto"
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:brightness-auto"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_set_select_rest(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)
    platform = get_select_platform(hass)
    state = hass.states.get(SELECT_ENTITY_ID_002)
    assert state.state == "auto"
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SelectEntity)
    # init_integration uses REST-API, which cannot write
    with pytest.raises(HomeAssistantError) as exc_info:
        await entity.async_select_option(entity.options[0])
    assert isinstance(exc_info.value.__cause__, XthermaReadOnlyError)


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    provide_modbus_data(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
async def test_set_select_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)
    platform = get_select_platform(hass)
    state = hass.states.get(SELECT_ENTITY_ID_MODBUS_002)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SelectEntity)
    await entity.async_select_option(entity.options[0])
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 1
    assert kwargs["value"] == 0
    assert kwargs["slave"] == 1
