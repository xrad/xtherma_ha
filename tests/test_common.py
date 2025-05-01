from pytest_homeassistant_custom_component.common import load_json_value_fixture

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
    assert len(telemetry) == 46
    t0 = telemetry[0]
    assert isinstance(t0, dict)
    assert t0.get("key") == "tvl"
    assert t0.get("input_factor") == "/10"
    t45 = telemetry[45]
    assert isinstance(t45, dict)
    assert t45.get("key") == "day_backup6_in_h"
    assert t45.get("input_factor") == "/100"
