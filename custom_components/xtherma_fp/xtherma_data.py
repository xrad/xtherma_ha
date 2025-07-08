"""Global data for integration."""

from .coordinator import XthermaDataUpdateCoordinator


class XthermaData:
    """Global data for integration."""

    coordinator: XthermaDataUpdateCoordinator | None = None
    sensors_initialized: bool = False
    switches_initialized: bool = False
    numbers_initialized: bool = False
    serial_fp: str = "()"
