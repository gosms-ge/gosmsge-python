"""Tests for response type dataclasses."""
from gosms.types import (
    BalanceResponse,
    BulkSmsResult,
    CheckStatusResponse,
    OtpSendResponse,
    OtpVerifyResponse,
    SendBulkSmsResponse,
    SenderCreateResponse,
    SmsSendResponse,
)


class TestSmsSendResponse:
    def test_from_dict(self, mock_send_response):
        resp = SmsSendResponse.from_dict(mock_send_response)
        assert resp.success is True
        assert resp.message_id == 12345
        assert resp.sender == "GOSMS"
        assert resp.to == "995555123456"
        assert resp.text == "Hello!"
        assert resp.balance == 100
        assert resp.send_at == "2025-01-15T10:30:00.000Z"

    def test_from_empty_dict(self):
        resp = SmsSendResponse.from_dict({})
        assert resp.success is False
        assert resp.message_id == 0
        assert resp.sender == ""
        assert resp.balance == 0

    def test_frozen(self, mock_send_response):
        resp = SmsSendResponse.from_dict(mock_send_response)
        import dataclasses
        with __import__("pytest").raises(dataclasses.FrozenInstanceError):
            resp.success = False  # type: ignore


class TestSendBulkSmsResponse:
    def test_from_dict(self, mock_bulk_response):
        resp = SendBulkSmsResponse.from_dict(mock_bulk_response)
        assert resp.success is True
        assert resp.total_count == 2
        assert resp.success_count == 2
        assert resp.failed_count == 0
        assert resp.balance == 98
        assert len(resp.messages) == 2
        assert resp.messages[0].message_id == 100
        assert resp.messages[1].to == "995555222222"

    def test_empty_messages(self):
        resp = SendBulkSmsResponse.from_dict({"success": True, "totalCount": 0})
        assert resp.messages == []


class TestBulkSmsResult:
    def test_from_dict(self):
        resp = BulkSmsResult.from_dict({"messageId": 42, "to": "995555111111", "success": True})
        assert resp.message_id == 42
        assert resp.success is True
        assert resp.error is None

    def test_with_error(self):
        resp = BulkSmsResult.from_dict({"messageId": 0, "to": "invalid", "success": False, "error": "Invalid phone"})
        assert resp.success is False
        assert resp.error == "Invalid phone"


class TestCheckStatusResponse:
    def test_from_dict(self, mock_status_response):
        resp = CheckStatusResponse.from_dict(mock_status_response)
        assert resp.success is True
        assert resp.message_id == 12345
        assert resp.status == "delivered"
        assert resp.sender == "GOSMS"


class TestBalanceResponse:
    def test_from_dict(self, mock_balance_response):
        resp = BalanceResponse.from_dict(mock_balance_response)
        assert resp.success is True
        assert resp.balance == 500

    def test_from_empty_dict(self):
        resp = BalanceResponse.from_dict({})
        assert resp.success is False
        assert resp.balance == 0


class TestOtpSendResponse:
    def test_from_dict(self, mock_otp_send_response):
        resp = OtpSendResponse.from_dict(mock_otp_send_response)
        assert resp.success is True
        assert resp.hash == "abc123hash"
        assert resp.balance == 99
        assert resp.to == "995555123456"


class TestOtpVerifyResponse:
    def test_verified(self):
        resp = OtpVerifyResponse.from_dict({"success": True, "verify": True})
        assert resp.verify is True

    def test_not_verified(self):
        resp = OtpVerifyResponse.from_dict({"success": True, "verify": False})
        assert resp.verify is False


class TestSenderCreateResponse:
    def test_from_dict(self, mock_sender_create_response):
        resp = SenderCreateResponse.from_dict(mock_sender_create_response)
        assert resp.success is True
