"""Tests for Django integration."""
from unittest.mock import MagicMock, patch

import pytest


class TestGetSmsClient:
    def setup_method(self):
        import gosms.django as mod

        mod.reset_client()

    def test_creates_client_from_settings(self):
        mock_settings = MagicMock()
        mock_settings.GOSMS_SETTINGS = {"api_key": "django_key", "timeout": 10}
        mock_settings.DEBUG = True

        import gosms.django as django_mod

        with patch.object(django_mod, "_get_settings", return_value=mock_settings):
            django_mod.reset_client()
            client = django_mod.get_sms_client()
            assert client._api_key == "django_key"
            assert client._timeout == 10
            assert client._debug is True

    def test_returns_singleton(self):
        mock_settings = MagicMock()
        mock_settings.GOSMS_SETTINGS = {"api_key": "key1"}
        mock_settings.DEBUG = False

        import gosms.django as django_mod

        with patch.object(django_mod, "_get_settings", return_value=mock_settings):
            django_mod.reset_client()
            client1 = django_mod.get_sms_client()
            client2 = django_mod.get_sms_client()
            assert client1 is client2

    def test_missing_api_key_raises(self):
        mock_settings = MagicMock()
        mock_settings.GOSMS_SETTINGS = {}

        import gosms.django as django_mod

        with (
            patch.object(django_mod, "_get_settings", return_value=mock_settings),
            patch.object(django_mod, "_get_improperly_configured", return_value=Exception),
        ):
            django_mod.reset_client()
            with pytest.raises(Exception, match="api_key"):
                django_mod.get_sms_client()

    def test_reset_client(self):
        import gosms.django as mod

        mod.reset_client()
        assert mod._client is None
