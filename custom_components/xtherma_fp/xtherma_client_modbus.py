"""Client to access Modbus server on Xtherma FP module."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.helpers.entity import EntityDescription

from custom_components.xtherma_fp.const import (
    KEY_ENTRY_INPUT_FACTOR,
    KEY_ENTRY_KEY,
    KEY_ENTRY_VALUE,
)
from custom_components.xtherma_fp.sensor_descriptors import (
    MODBUS_SENSOR_DESCRIPTIONS,
    XtSensorEntityDescription,
)

from .vendor.pymodbus import (
    AsyncModbusTcpClient,
    ModbusIOException,
)
from .xtherma_client_common import (
    XthermaClient,
    XthermaModbusError,
    XthermaNotConnectedError,
)

_LOGGER = logging.getLogger(__name__)

MODBUS_START_ADDRESS = 0
MODBUS_NUM_REGISTERS = 10


class XthermaClientModbus(XthermaClient):
    """Modbus access client."""

    _client: AsyncModbusTcpClient | None = None

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
        return timedelta(seconds=60)

    # apply two's complement for negative values. For now, only temperatures can be
    # negative.
    def _decode_int(self, raw_value: int, desc: EntityDescription) -> int:
        if (
            desc.device_class == SensorDeviceClass.TEMPERATURE and raw_value > 32767  # noqa: PLR2004
        ):
            return raw_value - 65536
        return raw_value

    async def _get_client(self) -> AsyncModbusTcpClient:
        if self._client is None or not self._client.connected:
            _LOGGER.debug("not connected, try connecting")
            await self.connect()
            # the following check is only for safety and ruff, self.connect() will have
            # alredy raised an exception if the reconnect fails
            if self._client is None or not self._client.connected:
                raise XthermaNotConnectedError
        return self._client

    async def async_get_data(self) -> list[dict[str, Any]]:
        """Obtain fresh data."""
        result: list[dict[str, Any]] = []
        client = await self._get_client()
        try:
            for reg_desc in MODBUS_SENSOR_DESCRIPTIONS:
                regs = await client.read_holding_registers(
                    address=reg_desc.base,
                    count=len(reg_desc.descriptors),
                    slave=int(self._address),
                )
                for i, desc in enumerate(reg_desc.descriptors):
                    if not desc:
                        _LOGGER.debug("no descriptor for %d.%d", reg_desc.base, i)
                    else:
                        entry = {}
                        entry[KEY_ENTRY_KEY] = desc.key
                        value = self._decode_int(regs.registers[i], desc)
                        entry[KEY_ENTRY_VALUE] = str(value)
                        if isinstance(desc, XtSensorEntityDescription):
                            entry[KEY_ENTRY_INPUT_FACTOR] = desc.factor
                        else:
                            entry[KEY_ENTRY_INPUT_FACTOR] = None
                        result.append(entry)
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
            return result

    def find_description(self, key) -> EntityDescription | None:
        """Find entity description for a given key."""
        for reg_desc in MODBUS_SENSOR_DESCRIPTIONS:
            for desc in reg_desc.descriptors:
                if desc is not None and desc.key.lower() == key.lower():
                    return desc
        return None
