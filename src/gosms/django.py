"""Django integration for GoSMS.GE SDK."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from gosms.client import SMS

_client: SMS | None = None


class _ImproperlyConfigured(Exception):
    """Fallback when Django is not installed."""


def _get_settings() -> Any:
    """Import and return Django settings. Separated for testability."""
    from django.conf import settings

    return settings


def _get_improperly_configured() -> type:
    """Import and return Django's ImproperlyConfigured exception."""
    try:
        from django.core.exceptions import ImproperlyConfigured

        return ImproperlyConfigured
    except ImportError:
        return _ImproperlyConfigured


def get_sms_client(**overrides: Any) -> SMS:
    """Get or create a singleton SMS client configured from Django settings.

    Reads from ``settings.GOSMS_SETTINGS``::

        # settings.py
        GOSMS_SETTINGS = {
            'api_key': 'your_key',
            'timeout': 30,      # optional
            'retries': 1,       # optional
            'debug': False,     # optional (defaults to DEBUG)
        }

    Usage::

        from gosms.django import get_sms_client
        sms = get_sms_client()
        sms.send('995555123456', 'Hello!', 'GOSMS.GE')
    """
    global _client
    if _client is None:
        from gosms.client import SMS

        settings = _get_settings()
        ImproperlyConfigured = _get_improperly_configured()

        config: dict[str, Any] = getattr(settings, "GOSMS_SETTINGS", {})
        api_key = config.get("api_key")
        if not api_key:
            raise ImproperlyConfigured(
                "GOSMS_SETTINGS must contain 'api_key'. "
                "Add GOSMS_SETTINGS = {'api_key': '...'} to your Django settings."
            )

        opts: dict[str, Any] = {
            "timeout": config.get("timeout", 30),
            "retries": config.get("retries", 1),
            "debug": config.get("debug", getattr(settings, "DEBUG", False)),
        }
        opts.update(overrides)
        _client = SMS(api_key, **opts)
    return _client


def reset_client() -> None:
    """Reset the singleton client. Useful for testing."""
    global _client
    _client = None
