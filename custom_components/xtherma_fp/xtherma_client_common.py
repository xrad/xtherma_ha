"""Common definitions for Xtherma client variants."""

from abc import abstractmethod
from datetime import timedelta


class XthermaRateLimitError(Exception):
    """Exception indicating REST API was accessed to frequently."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("API is busy")


class XthermaGeneralError(Exception):
    """Exception indicating a general error."""

    def __init__(self, msg: str = "General error") -> None:
        """Class constructor."""
        super().__init__(msg)


class XthermaModbusError(Exception):
    """Exception indicating a modbus error."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("Modbus error")


class XthermaNotConnectedError(Exception):
    """Exception indicating the client is not connected."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("Not connected error")


class XthermaRestApiError(Exception):
    """Exception indicating a rest api error."""

    def __init__(self, code: int) -> None:
        """Class constructor."""
        super().__init__("General error")
        self.code = code


class XthermaTimeoutError(Exception):
    """Exception indicating a communication timeout."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("timeout")


class XthermaClient:
    """Base class for Xtherma clients."""

    @abstractmethod
    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        raise NotImplementedError

    @abstractmethod
    async def connect(self) -> None:
        """Connect client to server endpoint."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect client."""
        raise NotImplementedError

    @abstractmethod
    async def async_get_data(self) -> dict[str, dict]:
        """Obtain fresh data."""
        raise NotImplementedError
