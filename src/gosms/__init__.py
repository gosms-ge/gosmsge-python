"""GoSMS.GE Python SDK -- Official SMS gateway client."""
from gosms.client import SMS
from gosms.exceptions import GoSmsApiError, GoSmsErrorCode
from gosms.types import RateLimitInfo

__version__ = "2.1.0"
__all__ = ["SMS", "GoSmsApiError", "GoSmsErrorCode", "RateLimitInfo"]

try:
    from gosms.async_client import AsyncSMS  # noqa: F401

    __all__.append("AsyncSMS")
except ImportError:
    pass
