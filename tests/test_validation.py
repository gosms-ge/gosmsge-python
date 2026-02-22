"""Input validation tests for GoSMS.GE SDK."""
import pytest

from gosms import SMS


class TestConstructorValidation:
    def test_valid_api_key(self):
        sms = SMS("test_key")
        assert sms._api_key == "test_key"

    def test_empty_api_key_raises(self):
        with pytest.raises(TypeError, match="api_key is required"):
            SMS("")

    def test_none_api_key_raises(self):
        with pytest.raises(TypeError, match="api_key is required"):
            SMS(None)  # type: ignore

    def test_int_api_key_raises(self):
        with pytest.raises(TypeError, match="api_key must be a string"):
            SMS(123)  # type: ignore

    def test_default_options(self):
        sms = SMS("key")
        assert sms._timeout == 30
        assert sms._retries == 1
        assert sms._debug is False

    def test_custom_options(self):
        sms = SMS("key", timeout=10, retries=3, debug=True)
        assert sms._timeout == 10
        assert sms._retries == 3
        assert sms._debug is True

    def test_retries_minimum_one(self):
        sms = SMS("key", retries=0)
        assert sms._retries == 1


class TestMethodValidation:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.sms = SMS("test_key")

    def test_send_empty_phone_raises(self):
        with pytest.raises(TypeError, match="phone_number is required"):
            self.sms.send("", "text", "sender")

    def test_send_empty_text_raises(self):
        with pytest.raises(TypeError, match="text is required"):
            self.sms.send("995555123456", "", "sender")

    def test_send_empty_sender_raises(self):
        with pytest.raises(TypeError, match="sender_name is required"):
            self.sms.send("995555123456", "text", "")

    def test_send_bulk_empty_list_raises(self):
        with pytest.raises(TypeError, match="phone_numbers is required"):
            self.sms.send_bulk("sender", [], "text")

    def test_send_bulk_not_list_raises(self):
        with pytest.raises(TypeError, match="phone_numbers is required"):
            self.sms.send_bulk("sender", "not_a_list", "text")  # type: ignore

    def test_send_otp_empty_phone_raises(self):
        with pytest.raises(TypeError, match="phone_number is required"):
            self.sms.send_otp("")

    def test_verify_otp_empty_hash_raises(self):
        with pytest.raises(TypeError, match="hash is required"):
            self.sms.verify_otp("995555123456", "", "1234")

    def test_verify_otp_empty_code_raises(self):
        with pytest.raises(TypeError, match="code is required"):
            self.sms.verify_otp("995555123456", "hash", "")

    def test_create_sender_empty_name_raises(self):
        with pytest.raises(TypeError, match="name is required"):
            self.sms.create_sender("")
