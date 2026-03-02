"""Asynchronous SMS client using the httpx library."""
from __future__ import annotations

import asyncio
from dataclasses import replace
from typing import Any

import httpx

from gosms._base import _BaseClient
from gosms.types import (
    BalanceResponse,
    CheckStatusResponse,
    OtpSendResponse,
    OtpVerifyResponse,
    RateLimitInfo,
    SendBulkSmsResponse,
    SenderCreateResponse,
    SmsSendResponse,
)


class AsyncSMS(_BaseClient):
    """Asynchronous GoSMS.GE API client.

    Can be used as an async context manager::

        async with AsyncSMS('api_key') as sms:
            result = await sms.send('995555123456', 'Hello!', 'GOSMS.GE')

    Or standalone::

        sms = AsyncSMS('api_key')
        result = await sms.send('995555123456', 'Hello!', 'GOSMS.GE')
        await sms.close()
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: int = 30,
        retries: int = 1,
        debug: bool = False,
    ) -> None:
        super().__init__(api_key, timeout=timeout, retries=retries, debug=debug)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> AsyncSMS:
        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            headers={"Content-Type": "application/json"},
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def _make_request(self, endpoint: str, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
        url = self._build_url(endpoint)
        client = self._get_client()
        last_error: Exception | None = None

        for attempt in range(1, self._retries + 1):
            try:
                self._log(f"Request attempt {attempt}/{self._retries} to {endpoint}")
                response = await client.post(url, json=payload)
                data: dict[str, Any] = response.json()
                headers = dict(response.headers)
                self._log("Response:", data)
                return self._parse_response(data, response.status_code, headers), headers
            except Exception as exc:
                last_error = exc
                self._log(f"Attempt {attempt} failed:", exc)
                if attempt < self._retries:
                    delay = self._calculate_delay(attempt)
                    self._log(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)

        raise last_error  # type: ignore[misc]

    async def send(
        self,
        phone_number: str,
        text: str,
        sender_name: str,
        urgent: bool = False,
    ) -> SmsSendResponse:
        """Send an SMS message to a single recipient."""
        self._validate_phone_number(phone_number, "phone_number")
        self._validate_string(text, "text")
        self._validate_string(sender_name, "sender_name")

        payload = self._build_payload(to=phone_number, text=text, urgent=urgent)
        payload["from"] = sender_name

        data, _ = await self._make_request("sendsms", payload)
        return SmsSendResponse.from_dict(data)

    async def send_bulk(
        self,
        sender_name: str,
        phone_numbers: list[str],
        text: str,
        urgent: bool = False,
        no_sms_number: str | None = None,
    ) -> SendBulkSmsResponse:
        """Send an SMS message to multiple recipients (max 1000)."""
        self._validate_string(sender_name, "sender_name")
        if not isinstance(phone_numbers, list) or len(phone_numbers) == 0:
            raise TypeError("phone_numbers is required and must be a non-empty list")
        self._validate_string(text, "text")

        payload = self._build_payload(to=phone_numbers, text=text, urgent=urgent)
        payload["from"] = sender_name
        if no_sms_number is not None:
            payload["noSmsNumber"] = no_sms_number

        data, _ = await self._make_request("sendbulk", payload)
        return SendBulkSmsResponse.from_dict(data)

    async def send_otp(self, phone_number: str) -> OtpSendResponse:
        """Send an OTP (One-Time Password) SMS."""
        self._validate_phone_number(phone_number, "phone_number")

        data, headers = await self._make_request("otp/send", self._build_payload(phone=phone_number))
        resp = OtpSendResponse.from_dict(data)
        rate_limit = RateLimitInfo.from_headers(headers)
        if rate_limit:
            resp = replace(resp, rate_limit=rate_limit)
        return resp

    async def verify_otp(self, phone_number: str, hash: str, code: str) -> OtpVerifyResponse:
        """Verify an OTP code."""
        self._validate_phone_number(phone_number, "phone_number")
        self._validate_string(hash, "hash")
        self._validate_string(code, "code")

        data, headers = await self._make_request(
            "otp/verify",
            self._build_payload(phone=phone_number, hash=hash, code=code),
        )
        resp = OtpVerifyResponse.from_dict(data)
        rate_limit = RateLimitInfo.from_headers(headers)
        if rate_limit:
            resp = replace(resp, rate_limit=rate_limit)
        return resp

    async def status(self, message_id: int) -> CheckStatusResponse:
        """Check the delivery status of a sent SMS message."""
        data, _ = await self._make_request("checksms", self._build_payload(messageId=message_id))
        return CheckStatusResponse.from_dict(data)

    async def balance(self) -> BalanceResponse:
        """Check the current SMS balance of your account."""
        data, _ = await self._make_request("sms-balance", self._build_payload())
        return BalanceResponse.from_dict(data)

    async def create_sender(self, name: str) -> SenderCreateResponse:
        """Register a new sender name."""
        self._validate_string(name, "name")

        data, _ = await self._make_request("sender", self._build_payload(name=name))
        return SenderCreateResponse.from_dict(data)
