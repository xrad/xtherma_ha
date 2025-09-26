"""Global data for integration."""

from homeassistant.helpers.device_registry import (
    DeviceInfo,
)

from .coordinator import XthermaDataUpdateCoordinator


class XthermaData:
    """Global data for integration."""

    coordinator: XthermaDataUpdateCoordinator | None
    sensors_initialized: bool
    switches_initialized: bool
    numbers_initialized: bool
    selects_initialized: bool
    serial_fp: str
    device_info: DeviceInfo

    def __init__(self) -> None:
        """Constructor."""
        self.coordinator = None
        self.sensors_initialized = False
        self.switches_initialized = False
        self.numbers_initialized = False
        self.selects_initialized = False
        self.serial_fp = "()"
        self.device_info = DeviceInfo()
