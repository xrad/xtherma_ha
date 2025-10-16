from homeassistant.components.number import (
    NumberEntity,
)
import pytest

from custom_components.xtherma_fp.xtherma_client_common import XthermaReadOnlyError
from tests.helpers import find_number_state, get_number_platform, load_rest_response
from homeassistant.exceptions import HomeAssistantError


async def test_number_icon(hass, init_integration):
    platform = get_number_platform(hass)
    state = find_number_state(hass, init_integration, "451")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:thermometer"


async def test_set_number_rest(hass, init_integration):
    platform = get_number_platform(hass)
    state = find_number_state(hass, init_integration, "451")
    assert state.state == "33.0"
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, NumberEntity)
    # init_integration uses REST-API, which cannot write
    with pytest.raises(HomeAssistantError):
        await entity.async_set_native_value(entity.native_min_value)


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    load_rest_response(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
# check writing positive values
async def test_set_number_modbus(hass, init_modbus_integration, mock_modbus_tcp_client):
    platform = get_number_platform(hass)
    state = find_number_state(hass, init_modbus_integration, "451")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, NumberEntity)
    await entity.async_set_native_value(entity.native_min_value)
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs['address'] == 41
    assert entity.native_min_value == 16
    assert kwargs['value'] == entity.native_min_value
    assert kwargs['slave'] == 1

# check writing negative values as 2s complement
@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    load_rest_response(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
async def test_set_negative_number_modbus(hass, init_modbus_integration, mock_modbus_tcp_client):
    platform = get_number_platform(hass)
    state = find_number_state(hass, init_modbus_integration, "411")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, NumberEntity)
    await entity.async_set_native_value(entity.native_min_value)
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs['address'] == 31
    assert entity.native_min_value == -20
    assert kwargs['value'] == (20 ^ 65535) + 1
    assert kwargs['slave'] == 1

