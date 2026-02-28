"""Exceptions raised by the api."""


class HikApiError(Exception):
    """General HikApi exception."""


class ConnectError(HikApiError):
    """Error connecting to HikCentral Server."""


class UnauthorizedError(HikApiError):
    """Authentication failed."""


class RequestError(HikApiError):
    """Request error."""
