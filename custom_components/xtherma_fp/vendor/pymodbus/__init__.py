import sys
from pathlib import Path

# Update python.analysis.extraPaths in .vscode/settings.json if you change this.
# If changed, make sure subclasses in modbus_client are still valid!
sys.path.insert(0, str((Path(__file__).parent / "pymodbus-3.9.2").absolute()))

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse

sys.path.pop(0)

__all__ = [
    "AsyncModbusTcpClient",
    "ModbusException",
    "ExceptionResponse"
]
