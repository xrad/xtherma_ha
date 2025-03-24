from .coordinator import XthermaDataUpdateCoordinator

class XthermaData:
    coordinator: XthermaDataUpdateCoordinator
    sensors_initialized: bool
    serial_fp: str

    def __init__(self):
        self.coordinator = None
        self.sensors_initialized = False
        self.serial_fp = "()"

