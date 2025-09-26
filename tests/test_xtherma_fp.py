import asyncio
from datetime import timedelta
from unittest.mock import patch
from homeassistant.const import Platform

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
from tests.helpers import load_mock_data


async def test_async_setup_entry_old(hass, aioclient_mock):
    """Verify old config entries without CONF_CONNECTION work."""
    mock_data = load_mock_data("rest_response.json")
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
    verify_integration_entry(entry)


def verify_integration_entry(entry: ConfigEntry):
    assert isinstance(entry.runtime_data, XthermaData)
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.sensors_initialized


def verify_integration_sensors(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.sensors_initialized

    our_sensors = [
        state
        for state in hass.states.async_all(Platform.SENSOR)
        if state.entity_id.startswith("sensor.xtherma_fp")
    ]
    assert len(our_sensors) == 54


def verify_integration_switches(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.switches_initialized

    our_switches = [
        state
        for state in hass.states.async_all(Platform.SWITCH)
        if state.entity_id.startswith("switch.xtherma_fp")
    ]
    if entry.data[CONF_CONNECTION] == CONF_CONNECTION_RESTAPI:
        assert len(our_switches) == 6
    else:
        assert len(our_switches) == 7


def verify_integration_numbers(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.numbers_initialized

    our_numbers = [
        state
        for state in hass.states.async_all(Platform.NUMBER)
        if state.entity_id.startswith("number.xtherma_fp")
    ]
    if entry.data[CONF_CONNECTION] == CONF_CONNECTION_RESTAPI:
        assert len(our_numbers) == 22
    else:
        assert len(our_numbers) == 25


def verify_integration_selects(hass: HomeAssistant, entry: ConfigEntry):
    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data.selects_initialized

    our_selects = [
        state
        for state in hass.states.async_all(Platform.SELECT)
        if state.entity_id.startswith("select.xtherma_fp")
    ]
    if entry.data[CONF_CONNECTION] == CONF_CONNECTION_RESTAPI:
        assert len(our_selects) == 1
    else:
        assert len(our_selects) == 2


async def test_async_setup_entry_restapi_ok(hass, aioclient_mock):
    """Verify config entries for REST API work."""
    mock_data = load_mock_data("rest_response.json")
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

    verify_integration_entry(entry)

    verify_integration_sensors(hass, entry)

    verify_integration_switches(hass, entry)

    verify_integration_numbers(hass, entry)

    verify_integration_selects(hass, entry)


async def test_async_setup_entry_restapi_delay(hass, aioclient_mock):
    """Verify config entries for REST API work."""
    # set up mock responses to simulate that initial response is is invalid
    # and we have to wait for the next refresh
    mock_data = load_mock_data("rest_response.json")
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
        assert isinstance(entry.runtime_data, XthermaData)

        # Verify sensors are not yet initialized
        xtherma_data: XthermaData = entry.runtime_data
        assert not xtherma_data.sensors_initialized

        # wait a bit more than one second for next coordinator update
        await asyncio.sleep(1.5)

        verify_integration_sensors(hass, entry)

        verify_integration_switches(hass, entry)

        verify_integration_numbers(hass, entry)

        verify_integration_selects(hass, entry)
