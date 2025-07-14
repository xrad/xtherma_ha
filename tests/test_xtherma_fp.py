import asyncio
from datetime import timedelta
from unittest.mock import patch

from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    load_json_value_fixture,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    MockLongPollSideEffect,
)

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
)
from custom_components.xtherma_fp.xtherma_data import XthermaData
from tests.const import MOCK_API_KEY, MOCK_SERIAL_NUMBER


async def test_async_setup_entry_old(hass, aioclient_mock):
    """Verify old config entries without CONF_CONNECTION work."""
    mock_data = load_json_value_fixture("rest_response.json")
    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    aioclient_mock.get(url, json=mock_data)

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: MOCK_API_KEY,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
        entry_id="test_entry_xtherma",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Verify setup worked
    _verify_entry(entry)


def _verify_entry(entry: ConfigEntry):
    assert isinstance(entry.runtime_data, XthermaData)


def _verify_sensors(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.sensors_initialized

    our_sensors = [
        state
        for state in hass.states.async_all("sensor")
        if state.entity_id.startswith("sensor.xtherma_fp")
    ]
    assert len(our_sensors) == 53

    # check first sensor state
    state = our_sensors[0]
    assert state.state == "22.1"
    assert state.entity_id == "sensor.xtherma_fp_tvl"
    assert state.attributes["device_class"] == SensorDeviceClass.TEMPERATURE
    assert state.attributes["unit_of_measurement"] == "°C"

    # check last sensor state
    state = our_sensors[len(our_sensors) - 1]
    assert state.entity_id == "sensor.xtherma_fp_mode"
    assert state.state == "water"


async def test_async_setup_entry_restapi_ok(hass, aioclient_mock):
    """Verify config entries for REST API work."""
    mock_data = load_json_value_fixture("rest_response.json")
    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    aioclient_mock.get(url, json=mock_data)
    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_API_KEY: MOCK_API_KEY,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
        entry_id="test_entry_xtherma",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Verify setup worked
    _verify_entry(entry)

    # Verify sensors are initialized
    _verify_sensors(hass, entry)


async def test_async_setup_entry_restapi_delay(hass, aioclient_mock):
    """Verify config entries for REST API work."""
    # set up mock responses to simulate that initial response is is invalid
    # and we have to wait for the next refresh
    mock_data = load_json_value_fixture("rest_response.json")
    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    side_effect = MockLongPollSideEffect()
    side_effect.queue_response(status=429)
    side_effect.queue_response(json=mock_data)
    aioclient_mock.get(url, side_effect=side_effect)

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_API_KEY: MOCK_API_KEY,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
        entry_id="test_entry_xtherma",
    )
    entry.add_to_hass(hass)

    # patch code to shorten update interval to 1 second for testing
    with patch(
        "custom_components.xtherma_fp.XthermaClientRest.update_interval",
        return_value=timedelta(seconds=1),
    ):
        # Call async_setup_entry()
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Verify setup worked
        _verify_entry(entry)

        # Verify sensors are not yet initialized
        xtherma_data: XthermaData = entry.runtime_data
        assert not xtherma_data.sensors_initialized

        # wait a bit more than one second for next coordinator update
        await asyncio.sleep(1.5)

        # Verify sensors have now been initialized
        _verify_sensors(hass, entry)
