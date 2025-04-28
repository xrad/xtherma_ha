"""Global data for integration."""

from .coordinator import XthermaDataUpdateCoordinator


class XthermaData:
    """Global data for integration."""

    coordinator: XthermaDataUpdateCoordinator | None
    sensors_initialized: bool
    serial_fp: str

    def __init__(self) -> None:
        """XthermaData constructor."""
        self.coordinator = None
        self.sensors_initialized = False
        self.serial_fp = "()"
