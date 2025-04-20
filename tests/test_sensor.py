import pytest

from homeassistant.core import State, HomeAssistant
from homeassistant.helpers.entity_platform import async_get_platforms

from custom_components.xtherma_fp.const import DOMAIN

async def _find_state(hass: HomeAssistant, id: str) -> State:
    full_id = f"sensor.xtherma_fp_{id}"
    state = hass.states.get(full_id)
    assert state is not None
    return state

#def _get_entity(hass: HomeAssistant, state: State) -> Entity:

@pytest.mark.asyncio
async def test_binary_sensor_state(hass, init_integration):
    pk = await _find_state(hass, "pk")
    assert pk.state == "off"
    pww = await _find_state(hass, "pww")
    assert pww.state == "on"

async def test_binary_sensor_icon(hass, init_integration):
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 1
    platform = platforms[0]
    pk = await _find_state(hass, "pk")
    assert pk.state == "off"
    e_pk = platform.entities.get(pk.entity_id)
    assert e_pk is not None
    assert e_pk.icon == "mdi:pump-off"
    pww = await _find_state(hass, "pww")
    assert pww.state == "on"
    e_pww = platform.entities.get(pww.entity_id)
    assert e_pww is not None
    assert e_pww.icon == "mdi:pump"

async def test_opmode_sensor_icon(hass, init_integration):
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 1
    platform = platforms[0]
    state = await _find_state(hass, "mode_3")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:thermometer-water"

async def test_sgready_sensor_icon(hass, init_integration):
    platforms = async_get_platforms(hass, DOMAIN)
    assert len(platforms) == 1
    platform = platforms[0]
    state = await _find_state(hass, "sg")
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert entity.icon == "mdi:circle-outline"
