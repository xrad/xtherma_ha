"""Constants for the Xtherma integration."""

import logging

DOMAIN = "xtherma_fp"

# current version of integration
VERSION = 1
MINOR_VERSION = 0

MANUFACTURER = "Xtherma"

# configuration keys.
# CONF_API_KEY is already defined by homeassistant.const
CONF_CONNECTION = "connection"
CONF_SERIAL_NUMBER = "serial_number"

# connection variants
CONF_CONNECTION_RESTAPI = "rest_api"
CONF_CONNECTION_MODBUSTCP = "modbus_tcp"

FERNPORTAL_URL = "https://fernportal.xtherma.de/api/device"

# Fernportal is rate limited to 1500 requests per day, one per minute
FERNPORTAL_RATE_LIMIT_S = 61

# keys in the response data

# element on top level
KEY_SERNO = "serial_number"
KEY_TELEMETRY = "telemetry"
KEY_SETTINGS = "settings"

# data entry keys in data and db_data
KEY_ENTRY_KEY = "key"
KEY_ENTRY_NAME = "name"
KEY_ENTRY_VALUE = "value"
KEY_ENTRY_MIN = "min"
KEY_ENTRY_MAX = "max"
KEY_ENTRY_MAPPING = "mapping"
KEY_ENTRY_UNIT = "unit"
KEY_ENTRY_OUTPUT_FACTOR = "output_factor"
KEY_ENTRY_INPUT_FACTOR = "input_factor"

LOGGER = logging.getLogger(__package__)
