"""Comprehensive tests for the synchronous SMS client."""
import json

import pytest
import requests
import responses

from gosms import SMS, GoSmsApiError, GoSmsErrorCode
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


class TestSend:
    @responses.activate
    def test_send_success(self, api_key, mock_send_response):
        responses.add(responses.POST, f"{BASE_URL}/sendsms", json=mock_send_response, status=200)
        sms = SMS(api_key)

        result = sms.send("995555123456", "Hello!", "GOSMS")

        assert isinstance(result, SmsSendResponse)
        assert result.success is True
        assert result.message_id == 12345
        assert result.sender == "GOSMS"
        assert result.to == "995555123456"
        assert result.balance == 100

    @responses.activate
    def test_send_urgent(self, api_key, mock_send_response):
        responses.add(responses.POST, f"{BASE_URL}/sendsms", json=mock_send_response, status=200)
        sms = SMS(api_key)

        sms.send("995555123456", "Urgent!", "GOSMS", urgent=True)

        body = json.loads(responses.calls[0].request.body)
        assert body["urgent"] is True

    @responses.activate
    def test_send_payload_correct(self, api_key, mock_send_response):
        responses.add(responses.POST, f"{BASE_URL}/sendsms", json=mock_send_response, status=200)
        sms = SMS(api_key)

        sms.send("995555123456", "Hello!", "GOSMS")

        body = json.loads(responses.calls[0].request.body)
        assert body["api_key"] == api_key
        assert body["to"] == "995555123456"
        assert body["text"] == "Hello!"
        assert body["from"] == "GOSMS"

    @responses.activate
    def test_send_api_error(self, api_key, mock_error_response):
        responses.add(responses.POST, f"{BASE_URL}/sendsms", json=mock_error_response, status=401)
        sms = SMS(api_key)

        with pytest.raises(GoSmsApiError) as exc_info:
            sms.send("995555123456", "Hello!", "GOSMS")

        assert exc_info.value.error_code == 100
        assert exc_info.value.message == "Invalid API key"

    @responses.activate
    def test_send_api_error_in_200(self, api_key):
        responses.add(
            responses.POST, f"{BASE_URL}/sendsms",
            json={"errorCode": 102, "message": "Insufficient balance"}, status=200,
        )
        sms = SMS(api_key)

        with pytest.raises(GoSmsApiError) as exc_info:
            sms.send("995555123456", "Hello!", "GOSMS")

        assert exc_info.value.error_code == 102


class TestSendBulk:
    @responses.activate
    def test_send_bulk_success(self, api_key, mock_bulk_response):
        responses.add(responses.POST, f"{BASE_URL}/sendbulk", json=mock_bulk_response, status=200)
        sms = SMS(api_key)

        result = sms.send_bulk("GOSMS", ["995555111111", "995555222222"], "Bulk hello")

        assert isinstance(result, SendBulkSmsResponse)
        assert result.success is True
        assert result.total_count == 2
        assert result.success_count == 2
        assert len(result.messages) == 2

    @responses.activate
    def test_send_bulk_with_no_sms_number(self, api_key, mock_bulk_response):
        responses.add(responses.POST, f"{BASE_URL}/sendbulk", json=mock_bulk_response, status=200)
        sms = SMS(api_key)

        sms.send_bulk("GOSMS", ["995555111111"], "text", no_sms_number="995322000000")

        body = json.loads(responses.calls[0].request.body)
        assert body["noSmsNumber"] == "995322000000"

    @responses.activate
    def test_send_bulk_without_no_sms_number(self, api_key, mock_bulk_response):
        responses.add(responses.POST, f"{BASE_URL}/sendbulk", json=mock_bulk_response, status=200)
        sms = SMS(api_key)

        sms.send_bulk("GOSMS", ["995555111111"], "text")

        body = json.loads(responses.calls[0].request.body)
        assert "noSmsNumber" not in body

    @responses.activate
    def test_send_bulk_payload(self, api_key, mock_bulk_response):
        responses.add(responses.POST, f"{BASE_URL}/sendbulk", json=mock_bulk_response, status=200)
        sms = SMS(api_key)

        sms.send_bulk("GOSMS", ["995555111111", "995555222222"], "Hello", urgent=True)

        body = json.loads(responses.calls[0].request.body)
        assert body["from"] == "GOSMS"
        assert body["to"] == ["995555111111", "995555222222"]
        assert body["text"] == "Hello"
        assert body["urgent"] is True


class TestSendOtp:
    @responses.activate
    def test_send_otp_success(self, api_key, mock_otp_send_response):
        responses.add(responses.POST, f"{BASE_URL}/otp/send", json=mock_otp_send_response, status=200)
        sms = SMS(api_key)

        result = sms.send_otp("995555123456")

        assert isinstance(result, OtpSendResponse)
        assert result.success is True
        assert result.hash == "abc123hash"
        assert result.balance == 99

    @responses.activate
    def test_send_otp_payload(self, api_key, mock_otp_send_response):
        responses.add(responses.POST, f"{BASE_URL}/otp/send", json=mock_otp_send_response, status=200)
        sms = SMS(api_key)

        sms.send_otp("995555123456")

        body = json.loads(responses.calls[0].request.body)
        assert body["phone"] == "995555123456"
        assert body["api_key"] == api_key


class TestVerifyOtp:
    @responses.activate
    def test_verify_otp_success(self, api_key, mock_otp_verify_response):
        responses.add(responses.POST, f"{BASE_URL}/otp/verify", json=mock_otp_verify_response, status=200)
        sms = SMS(api_key)

        result = sms.verify_otp("995555123456", "abc123hash", "1234")

        assert isinstance(result, OtpVerifyResponse)
        assert result.success is True
        assert result.verify is True

    @responses.activate
    def test_verify_otp_invalid_code(self, api_key):
        responses.add(
            responses.POST, f"{BASE_URL}/otp/verify",
            json={"success": True, "verify": False}, status=200,
        )
        sms = SMS(api_key)

        result = sms.verify_otp("995555123456", "abc123hash", "0000")

        assert result.verify is False

    @responses.activate
    def test_verify_otp_payload(self, api_key, mock_otp_verify_response):
        responses.add(responses.POST, f"{BASE_URL}/otp/verify", json=mock_otp_verify_response, status=200)
        sms = SMS(api_key)

        sms.verify_otp("995555123456", "myhash", "4321")

        body = json.loads(responses.calls[0].request.body)
        assert body["phone"] == "995555123456"
        assert body["hash"] == "myhash"
        assert body["code"] == "4321"


class TestStatus:
    @responses.activate
    def test_status_success(self, api_key, mock_status_response):
        responses.add(responses.POST, f"{BASE_URL}/checksms", json=mock_status_response, status=200)
        sms = SMS(api_key)

        result = sms.status(12345)

        assert isinstance(result, CheckStatusResponse)
        assert result.success is True
        assert result.message_id == 12345
        assert result.status == "delivered"

    @responses.activate
    def test_status_payload(self, api_key, mock_status_response):
        responses.add(responses.POST, f"{BASE_URL}/checksms", json=mock_status_response, status=200)
        sms = SMS(api_key)

        sms.status(12345)

        body = json.loads(responses.calls[0].request.body)
        assert body["messageId"] == 12345


class TestBalance:
    @responses.activate
    def test_balance_success(self, api_key, mock_balance_response):
        responses.add(responses.POST, f"{BASE_URL}/sms-balance", json=mock_balance_response, status=200)
        sms = SMS(api_key)

        result = sms.balance()

        assert isinstance(result, BalanceResponse)
        assert result.success is True
        assert result.balance == 500


class TestCreateSender:
    @responses.activate
    def test_create_sender_success(self, api_key, mock_sender_create_response):
        responses.add(responses.POST, f"{BASE_URL}/sender", json=mock_sender_create_response, status=200)
        sms = SMS(api_key)

        result = sms.create_sender("MyBrand")

        assert isinstance(result, SenderCreateResponse)
        assert result.success is True

    @responses.activate
    def test_create_sender_payload(self, api_key, mock_sender_create_response):
        responses.add(responses.POST, f"{BASE_URL}/sender", json=mock_sender_create_response, status=200)
        sms = SMS(api_key)

        sms.create_sender("MyBrand")

        body = json.loads(responses.calls[0].request.body)
        assert body["name"] == "MyBrand"
        assert body["api_key"] == api_key

    @responses.activate
    def test_create_sender_api_error(self, api_key):
        responses.add(
            responses.POST, f"{BASE_URL}/sender",
            json={"errorCode": 107, "message": "Sender name already exists"}, status=200,
        )
        sms = SMS(api_key)

        with pytest.raises(GoSmsApiError) as exc_info:
            sms.create_sender("ExistingBrand")

        assert exc_info.value.error_code == GoSmsErrorCode.SENDER_EXISTS


class TestErrorHandling:
    @responses.activate
    def test_network_error(self, api_key):
        responses.add(
            responses.POST, f"{BASE_URL}/sms-balance",
            body=ConnectionError("Connection refused"),
        )
        sms = SMS(api_key)

        with pytest.raises(ConnectionError):
            sms.balance()

    @responses.activate
    def test_http_500_without_json_error(self, api_key):
        responses.add(responses.POST, f"{BASE_URL}/sms-balance", body="Server Error", status=500)
        sms = SMS(api_key)

        with pytest.raises((ValueError, requests.exceptions.JSONDecodeError)):
            sms.balance()

    @responses.activate
    def test_error_repr(self, api_key, mock_error_response):
        responses.add(responses.POST, f"{BASE_URL}/sms-balance", json=mock_error_response, status=401)
        sms = SMS(api_key)

        with pytest.raises(GoSmsApiError) as exc_info:
            sms.balance()

        assert "100" in str(exc_info.value)
        assert "Invalid API key" in str(exc_info.value)
        assert "GoSmsApiError" in repr(exc_info.value)


class TestRetryLogic:
    @responses.activate
    def test_retry_on_failure_then_success(self, api_key, mock_balance_response):
        responses.add(responses.POST, f"{BASE_URL}/sms-balance", body=ConnectionError("fail"))
        responses.add(responses.POST, f"{BASE_URL}/sms-balance", json=mock_balance_response, status=200)
        sms = SMS(api_key, retries=2)

        result = sms.balance()

        assert result.success is True
        assert len(responses.calls) == 2

    @responses.activate
    def test_exhaust_retries(self, api_key):
        responses.add(responses.POST, f"{BASE_URL}/sms-balance", body=ConnectionError("fail"))
        responses.add(responses.POST, f"{BASE_URL}/sms-balance", body=ConnectionError("fail again"))
        sms = SMS(api_key, retries=2)

        with pytest.raises(ConnectionError):
            sms.balance()

        assert len(responses.calls) == 2

    @responses.activate
    def test_single_retry_default(self, api_key):
        responses.add(responses.POST, f"{BASE_URL}/sms-balance", body=ConnectionError("fail"))
        sms = SMS(api_key)  # default retries=1

        with pytest.raises(ConnectionError):
            sms.balance()

        assert len(responses.calls) == 1


class TestDebugMode:
    @responses.activate
    def test_debug_logging(self, api_key, mock_balance_response, caplog):
        responses.add(responses.POST, f"{BASE_URL}/sms-balance", json=mock_balance_response, status=200)
        sms = SMS(api_key, debug=True)

        import logging
        with caplog.at_level(logging.DEBUG, logger="gosms"):
            sms.balance()

        assert any("GOSMS Debug" in r.message for r in caplog.records)
