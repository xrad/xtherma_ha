"""Common tests."""

from pytest_homeassistant_custom_component.common import load_json_value_fixture

from custom_components.xtherma_fp.const import KEY_ENTRY_INPUT_FACTOR
from custom_components.xtherma_fp.entity_descriptors import (
    MODBUS_ENTITY_DESCRIPTIONS,
    XtNumericEntityDescription,
)
from tests.helpers import find_entry, flatten_mock_data, load_mock_data


def test_json_load_value_fixture():
    data = load_json_value_fixture("rest_response.json")
    assert isinstance(data, dict)
    assert len(data) == 3
    assert data.get("serial_number") == "FP-04-123456"
    settings = data.get("settings")
    assert isinstance(settings, list)
    assert len(settings) == 34
    telemetry = data.get("telemetry")
    assert isinstance(telemetry, list)
    assert len(telemetry) == 54
    t0 = telemetry[0]
    assert isinstance(t0, dict)
    assert t0.get("key") == "tvl"
    assert t0.get("input_factor") == "/10"
    tlast = telemetry[53]
    assert isinstance(tlast, dict)
    assert tlast.get("key") == "mode"
    assert tlast.get("value") == "3"


def test_input_factors():
    """Verify that input_factors in REST response match Modbus descriptors."""
    mock_data = load_mock_data("rest_response.json")
    flattened_mock_data = flatten_mock_data(mock_data)
    for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
        for desc in reg_desc.descriptors:
            if not isinstance(desc, XtNumericEntityDescription):
                continue
            entry = find_entry(flattened_mock_data, desc.key)
            input_factor = entry.get(KEY_ENTRY_INPUT_FACTOR)
            if input_factor == "":
                assert desc.factor is None
            else:
                assert input_factor == desc.factor
