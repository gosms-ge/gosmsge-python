"""Exception types and error codes for the GoSMS.GE SDK."""
from __future__ import annotations


class GoSmsErrorCode:
    """Error code constants matching the GoSMS.GE API."""

    INVALID_API_KEY = 100
    INVALID_SENDER = 101
    INSUFFICIENT_BALANCE = 102
    INVALID_PARAMETERS = 103
    MESSAGE_NOT_FOUND = 104
    INVALID_PHONE = 105
    OTP_FAILED = 106
    SENDER_EXISTS = 107
    NOT_CONFIGURED = 108
    TOO_MANY_REQUESTS = 109
    ACCOUNT_LOCKED = 110
    OTP_EXPIRED = 111
    OTP_ALREADY_USED = 112
    INVALID_NO_SMS_NUMBER = 113


class GoSmsApiError(Exception):
    """Raised when the GoSMS.GE API returns an error response."""

    def __init__(self, error_code: int, message: str, retry_after: int | None = None) -> None:
        self.error_code = error_code
        self.message = message
        self.retry_after = retry_after
        super().__init__(f"[{error_code}] {message}")

    def __repr__(self) -> str:
        return f"GoSmsApiError(error_code={self.error_code}, message={self.message!r})"
