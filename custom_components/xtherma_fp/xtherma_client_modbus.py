"""Client to access Modbus server on Xtherma FP module."""

import re
from datetime import timedelta

from pymodbus.client import (
    AsyncModbusTcpClient,
)

from .const import LOGGER
from .xtherma_client_common import (
    XthermaClient,
    XthermaGeneralError,
    XthermaModbusError,
    XthermaNotConnectedError,
    XthermaTimeoutError,
)

MODBUS_START_ADDRESS = 10000
MODBUS_NUM_REGISTERS = 46


class XthermaClientModbus(XthermaClient):
    """Modbus access client."""

    _client: AsyncModbusTcpClient | None = None

    def __init__(self, host: str, port: int, address: int) -> None:
        """Class constructor."""
        self._host = host
        self._port = port
        self._address = address

    async def is_connected(self) -> bool:
        """Check if client is currently connected."""
        return self._client is AsyncModbusTcpClient and self._client.connected()

    async def connect(self) -> None:
        """Connect client to server endpoint."""
        self._client = AsyncModbusTcpClient(host=self._host, port=self._port)
        try:
            result = await self._client.connect()
        except Exception as err:
            LOGGER.error("Modbus error: %s", err)
            raise XthermaModbusError from err
        if not result:
            raise XthermaNotConnectedError

    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        return timedelta(seconds=10)

    async def async_get_data(self) -> dict[str, dict]:
        """Obtain fresh data."""
        if self._client is not AsyncModbusTcpClient:
            raise XthermaNotConnectedError
        try:
            result = self._client.read_holding_registers(
                address=MODBUS_START_ADDRESS,
                count=MODBUS_NUM_REGISTERS,
                slave=self._address,
            )
        except TimeoutError as err:
            LOGGER.error("Modbus request timed out")
            raise XthermaTimeoutError from err
        except Exception as err:
            LOGGER.error("Modbus error: %s", err)
            raise XthermaModbusError from err
        if result.isError():
            raise XthermaGeneralError(result.error)
        return {}
