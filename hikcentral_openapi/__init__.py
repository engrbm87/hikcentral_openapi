"""HikCentral Open API library."""

from .client import Client
from .exceptions import HikApiError

__all__ = ["Client", "HikApiError"]
