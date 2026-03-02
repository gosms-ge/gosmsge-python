"""Response type definitions matching the GoSMS.GE API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RateLimitInfo:
    """Rate limit information from OTP endpoint response headers."""

    limit: int | None = None
    remaining: int | None = None
    retry_after: int | None = None

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> RateLimitInfo | None:
        limit = headers.get("X-RateLimit-Limit")
        remaining = headers.get("X-RateLimit-Remaining")
        retry_after = headers.get("Retry-After")
        if limit is None and remaining is None and retry_after is None:
            return None
        return cls(
            limit=int(limit) if limit else None,
            remaining=int(remaining) if remaining else None,
            retry_after=int(retry_after) if retry_after else None,
        )


@dataclass(frozen=True)
class SmsSendResponse:
    success: bool
    message_id: int
    sender: str
    to: str
    text: str
    send_at: str
    balance: int
    encode: str
    segment: int
    sms_characters: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SmsSendResponse:
        return cls(
            success=data.get("success", False),
            message_id=data.get("messageId", 0),
            sender=data.get("from", ""),
            to=data.get("to", ""),
            text=data.get("text", ""),
            send_at=data.get("sendAt", ""),
            balance=data.get("balance", 0),
            encode=data.get("encode", ""),
            segment=data.get("segment", 0),
            sms_characters=data.get("smsCharacters", 0),
        )


@dataclass(frozen=True)
class BulkSmsResult:
    message_id: int
    to: str
    success: bool
    error: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BulkSmsResult:
        return cls(
            message_id=data.get("messageId", 0),
            to=data.get("to", ""),
            success=data.get("success", False),
            error=data.get("error"),
        )


@dataclass(frozen=True)
class SendBulkSmsResponse:
    success: bool
    total_count: int
    success_count: int
    failed_count: int
    balance: int
    sender: str
    text: str
    encode: str
    segment: int
    sms_characters: int
    messages: list[BulkSmsResult] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SendBulkSmsResponse:
        return cls(
            success=data.get("success", False),
            total_count=data.get("totalCount", 0),
            success_count=data.get("successCount", 0),
            failed_count=data.get("failedCount", 0),
            balance=data.get("balance", 0),
            sender=data.get("from", ""),
            text=data.get("text", ""),
            encode=data.get("encode", ""),
            segment=data.get("segment", 0),
            sms_characters=data.get("smsCharacters", 0),
            messages=[BulkSmsResult.from_dict(m) for m in data.get("messages", [])],
        )


@dataclass(frozen=True)
class CheckStatusResponse:
    success: bool
    message_id: int
    sender: str
    to: str
    text: str
    send_at: str
    encode: str
    segment: int
    sms_characters: int
    status: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CheckStatusResponse:
        return cls(
            success=data.get("success", False),
            message_id=data.get("messageId", 0),
            sender=data.get("from", ""),
            to=data.get("to", ""),
            text=data.get("text", ""),
            send_at=data.get("sendAt", ""),
            encode=data.get("encode", ""),
            segment=data.get("segment", 0),
            sms_characters=data.get("smsCharacters", 0),
            status=data.get("status", ""),
        )


@dataclass(frozen=True)
class BalanceResponse:
    success: bool
    balance: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BalanceResponse:
        return cls(
            success=data.get("success", False),
            balance=data.get("balance", 0),
        )


@dataclass(frozen=True)
class OtpSendResponse:
    success: bool
    hash: str
    balance: int
    to: str
    send_at: str
    encode: str
    segment: int
    sms_characters: int
    rate_limit: RateLimitInfo | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OtpSendResponse:
        return cls(
            success=data.get("success", False),
            hash=data.get("hash", ""),
            balance=data.get("balance", 0),
            to=data.get("to", ""),
            send_at=data.get("sendAt", ""),
            encode=data.get("encode", ""),
            segment=data.get("segment", 0),
            sms_characters=data.get("smsCharacters", 0),
        )


@dataclass(frozen=True)
class OtpVerifyResponse:
    success: bool
    verify: bool
    rate_limit: RateLimitInfo | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OtpVerifyResponse:
        return cls(
            success=data.get("success", False),
            verify=data.get("verify", False),
        )


@dataclass(frozen=True)
class SenderCreateResponse:
    success: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SenderCreateResponse:
        return cls(
            success=data.get("success", False),
        )
