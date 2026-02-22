"""Tests for the asynchronous AsyncSMS client."""
import json

import pytest

from gosms.async_client import AsyncSMS
from gosms.exceptions import GoSmsApiError
from gosms.types import (
    BalanceResponse,
    CheckStatusResponse,
    OtpSendResponse,
    OtpVerifyResponse,
    SendBulkSmsResponse,
    SenderCreateResponse,
    SmsSendResponse,
)

BASE_URL = "https://api.gosms.ge/api"


class TestAsyncSend:
    @pytest.mark.asyncio
    async def test_send_success(self, httpx_mock, api_key, mock_send_response):
        httpx_mock.add_response(url=f"{BASE_URL}/sendsms", json=mock_send_response)

        async with AsyncSMS(api_key) as sms:
            result = await sms.send("995555123456", "Hello!", "GOSMS")

        assert isinstance(result, SmsSendResponse)
        assert result.success is True
        assert result.message_id == 12345

    @pytest.mark.asyncio
    async def test_send_payload(self, httpx_mock, api_key, mock_send_response):
        httpx_mock.add_response(url=f"{BASE_URL}/sendsms", json=mock_send_response)

        async with AsyncSMS(api_key) as sms:
            await sms.send("995555123456", "Hello!", "GOSMS", urgent=True)

        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["api_key"] == api_key
        assert body["to"] == "995555123456"
        assert body["from"] == "GOSMS"
        assert body["urgent"] is True


class TestAsyncSendBulk:
    @pytest.mark.asyncio
    async def test_send_bulk_success(self, httpx_mock, api_key, mock_bulk_response):
        httpx_mock.add_response(url=f"{BASE_URL}/sendbulk", json=mock_bulk_response)

        async with AsyncSMS(api_key) as sms:
            result = await sms.send_bulk("GOSMS", ["995555111111", "995555222222"], "Bulk hello")

        assert isinstance(result, SendBulkSmsResponse)
        assert result.total_count == 2
        assert len(result.messages) == 2


class TestAsyncSendOtp:
    @pytest.mark.asyncio
    async def test_send_otp_success(self, httpx_mock, api_key, mock_otp_send_response):
        httpx_mock.add_response(url=f"{BASE_URL}/otp/send", json=mock_otp_send_response)

        async with AsyncSMS(api_key) as sms:
            result = await sms.send_otp("995555123456")

        assert isinstance(result, OtpSendResponse)
        assert result.hash == "abc123hash"


class TestAsyncVerifyOtp:
    @pytest.mark.asyncio
    async def test_verify_otp_success(self, httpx_mock, api_key, mock_otp_verify_response):
        httpx_mock.add_response(url=f"{BASE_URL}/otp/verify", json=mock_otp_verify_response)

        async with AsyncSMS(api_key) as sms:
            result = await sms.verify_otp("995555123456", "abc123hash", "1234")

        assert isinstance(result, OtpVerifyResponse)
        assert result.verify is True


class TestAsyncStatus:
    @pytest.mark.asyncio
    async def test_status_success(self, httpx_mock, api_key, mock_status_response):
        httpx_mock.add_response(url=f"{BASE_URL}/checksms", json=mock_status_response)

        async with AsyncSMS(api_key) as sms:
            result = await sms.status(12345)

        assert isinstance(result, CheckStatusResponse)
        assert result.status == "delivered"


class TestAsyncBalance:
    @pytest.mark.asyncio
    async def test_balance_success(self, httpx_mock, api_key, mock_balance_response):
        httpx_mock.add_response(url=f"{BASE_URL}/sms-balance", json=mock_balance_response)

        async with AsyncSMS(api_key) as sms:
            result = await sms.balance()

        assert isinstance(result, BalanceResponse)
        assert result.balance == 500


class TestAsyncCreateSender:
    @pytest.mark.asyncio
    async def test_create_sender_success(self, httpx_mock, api_key, mock_sender_create_response):
        httpx_mock.add_response(url=f"{BASE_URL}/sender", json=mock_sender_create_response)

        async with AsyncSMS(api_key) as sms:
            result = await sms.create_sender("MyBrand")

        assert isinstance(result, SenderCreateResponse)
        assert result.success is True


class TestAsyncErrorHandling:
    @pytest.mark.asyncio
    async def test_api_error(self, httpx_mock, api_key, mock_error_response):
        httpx_mock.add_response(url=f"{BASE_URL}/sms-balance", json=mock_error_response, status_code=401)

        async with AsyncSMS(api_key) as sms:
            with pytest.raises(GoSmsApiError) as exc_info:
                await sms.balance()

        assert exc_info.value.error_code == 100


class TestAsyncContextManager:
    @pytest.mark.asyncio
    async def test_context_manager(self, httpx_mock, api_key, mock_balance_response):
        httpx_mock.add_response(url=f"{BASE_URL}/sms-balance", json=mock_balance_response)

        async with AsyncSMS(api_key) as sms:
            result = await sms.balance()
            assert result.balance == 500

        # Client should be closed after exit
        assert sms._client is None

    @pytest.mark.asyncio
    async def test_standalone_usage(self, httpx_mock, api_key, mock_balance_response):
        httpx_mock.add_response(url=f"{BASE_URL}/sms-balance", json=mock_balance_response)

        sms = AsyncSMS(api_key)
        result = await sms.balance()
        assert result.balance == 500
        await sms.close()
        assert sms._client is None


class TestAsyncValidation:
    @pytest.mark.asyncio
    async def test_send_empty_phone_raises(self, api_key):
        sms = AsyncSMS(api_key)
        with pytest.raises(TypeError, match="phone_number is required"):
            await sms.send("", "text", "sender")

    @pytest.mark.asyncio
    async def test_send_bulk_empty_list_raises(self, api_key):
        sms = AsyncSMS(api_key)
        with pytest.raises(TypeError, match="phone_numbers is required"):
            await sms.send_bulk("sender", [], "text")
