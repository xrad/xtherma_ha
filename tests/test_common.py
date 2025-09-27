from pytest_homeassistant_custom_component.common import load_json_value_fixture

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import async_get_platforms, EntityPlatform

from custom_components.xtherma_fp.const import DOMAIN


async def get_platform(hass: HomeAssistant, domain: str) -> EntityPlatform:
    platforms = async_get_platforms(hass, DOMAIN)
    for platform in platforms:
        if platform.domain == domain:
            return platform
    raise Exception("Platform %s not found", domain)

def test_json_load_value_fixture():
    data = load_json_value_fixture("rest_response.json")
    assert isinstance(data, dict)
    assert len(data) == 3
    assert data.get("serial_number") == "FP-04-123456"
    settings = data.get("settings")
    assert isinstance(settings, list)
    assert len(settings) == 31
    telemetry = data.get("telemetry")
    assert isinstance(telemetry, list)
    assert len(telemetry) == 54
    t0 = telemetry[0]
    assert isinstance(t0, dict)
    assert t0.get("key") == "tvl"
    assert t0.get("input_factor") == "/10"
    tLast = telemetry[53]
    assert isinstance(tLast, dict)
    assert tLast.get("key") == "mode"
    assert tLast.get("value") == "3"
