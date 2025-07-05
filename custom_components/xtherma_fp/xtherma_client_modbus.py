"""Client to access Modbus server on Xtherma FP module."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.helpers.entity import EntityDescription
from pymodbus.client import (
    AsyncModbusTcpClient,
)
from pymodbus.exceptions import (
    ModbusIOException,
)

from custom_components.xtherma_fp.const import (
    KEY_ENTRY_INPUT_FACTOR,
    KEY_ENTRY_KEY,
    KEY_ENTRY_VALUE,
)
from custom_components.xtherma_fp.sensor_descriptors import (
    SENSOR_DESCRIPTIONS,
    XtSensorEntityDescription,
)

from .xtherma_client_common import (
    XthermaClient,
    XthermaModbusError,
    XthermaNotConnectedError,
)

_LOGGER = logging.getLogger(__name__)

MODBUS_START_ADDRESS = 0
MODBUS_NUM_REGISTERS = 10

def _find_modbus_desciptor(index: int) -> EntityDescription | None:
    for sensor in SENSOR_DESCRIPTIONS:
        if sensor.modbus_index == index:
            return sensor
    return None

class XthermaClientModbus(XthermaClient):
    """Modbus access client."""

    _client: AsyncModbusTcpClient | None = None
    _descriptors: list[EntityDescription|None]

    def __init__(
        self,
        host: str,
        port: int,
        address: int,
    ) -> None:
        """Class constructor."""
        self._host = host
        self._port = port
        self._address = address
        self._descriptors = []
        for i in range(MODBUS_NUM_REGISTERS):
            d = _find_modbus_desciptor(i)
            self._descriptors.append(d)

    async def connect(self) -> None:
        """Connect client to server endpoint."""
        self._client = AsyncModbusTcpClient(host=self._host, port=self._port)
        try:
            _LOGGER.debug("connecting client")
            result = await self._client.connect()
            _LOGGER.debug(
                "connected client success = %s, connected = %s",
                result,
                self._client.connected,
            )
        except Exception as err:
            _LOGGER.exception("connection error")
            raise XthermaNotConnectedError from err
        if not result:
            raise XthermaNotConnectedError

    async def disconnect(self) -> None:
        """Disconnect client."""
        if self._client:
            _LOGGER.debug("disconnect")
            self._client.close()
            self._client = None

    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        return timedelta(seconds=10)

    async def async_get_data(self) -> list[dict[str, Any]]:
        """Obtain fresh data."""
        if self._client is None or not self._client.connected:
            _LOGGER.debug("not connected")
            raise XthermaNotConnectedError
        try:
            regs = await self._client.read_holding_registers(
                address=MODBUS_START_ADDRESS,
                count=MODBUS_NUM_REGISTERS,
                slave=int(self._address),
            )
        except ModbusIOException as err:
            _LOGGER.error("Modbus error: %s", err.string)  # noqa: TRY400
            raise XthermaModbusError from err
        except Exception as err:
            _LOGGER.exception("Exception error")
            raise XthermaModbusError from err
        else:
            if regs.isError():
                _LOGGER.error("Modbus error %s", regs.exception_code)
                raise XthermaModbusError
            result: list[dict[str, Any]] = []
            for i in range(MODBUS_NUM_REGISTERS):
                d = self._descriptors[i]
                if d:
                    entry = {}
                    entry[KEY_ENTRY_KEY] = d.key
                    entry[KEY_ENTRY_VALUE] = regs.registers[i]
                    if isinstance(d, XtSensorEntityDescription):
                        entry[KEY_ENTRY_INPUT_FACTOR] = d.factor
                    else:
                        entry[KEY_ENTRY_INPUT_FACTOR] = None
                    result.append(entry)
            return result

    def find_description(self, key) -> EntityDescription | None:
        """Find entity description for a given key."""
        for reg_desc in MODBUS_SENSOR_DESCRIPTIONS:
            for desc in reg_desc.descriptors:
                if desc is not None and desc.key.lower() == key.lower():
                    return desc
        return None
