"""Shared test fixtures for GoSMS.GE SDK tests."""
import pytest

API_KEY = "test_api_key_123"
BASE_URL = "https://api.gosms.ge/api"


@pytest.fixture
def api_key() -> str:
    return API_KEY


@pytest.fixture
def mock_send_response() -> dict:
    return {
        "success": True,
        "messageId": 12345,
        "from": "GOSMS",
        "to": "995555123456",
        "text": "Hello!",
        "sendAt": "2025-01-15T10:30:00.000Z",
        "balance": 100,
        "encode": "default",
        "segment": 1,
        "smsCharacters": 6,
    }


@pytest.fixture
def mock_bulk_response() -> dict:
    return {
        "success": True,
        "totalCount": 2,
        "successCount": 2,
        "failedCount": 0,
        "balance": 98,
        "from": "GOSMS",
        "text": "Bulk hello",
        "encode": "default",
        "segment": 1,
        "smsCharacters": 10,
        "messages": [
            {"messageId": 100, "to": "995555111111", "success": True},
            {"messageId": 101, "to": "995555222222", "success": True},
        ],
    }


@pytest.fixture
def mock_status_response() -> dict:
    return {
        "success": True,
        "messageId": 12345,
        "from": "GOSMS",
        "to": "995555123456",
        "text": "Hello!",
        "sendAt": "2025-01-15T10:30:00.000Z",
        "encode": "default",
        "segment": 1,
        "smsCharacters": 6,
        "status": "delivered",
    }


@pytest.fixture
def mock_balance_response() -> dict:
    return {"success": True, "balance": 500}


@pytest.fixture
def mock_otp_send_response() -> dict:
    return {
        "success": True,
        "hash": "abc123hash",
        "balance": 99,
        "to": "995555123456",
        "sendAt": "2025-01-15T10:30:00.000Z",
        "encode": "default",
        "segment": 1,
        "smsCharacters": 6,
    }


@pytest.fixture
def mock_otp_verify_response() -> dict:
    return {"success": True, "verify": True}


@pytest.fixture
def mock_sender_create_response() -> dict:
    return {"success": True}


@pytest.fixture
def mock_error_response() -> dict:
    return {"errorCode": 100, "message": "Invalid API key"}
