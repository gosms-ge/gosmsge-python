"""Shared base logic for sync and async clients."""
from __future__ import annotations

import logging
from typing import Any

from gosms.exceptions import GoSmsApiError

logger = logging.getLogger("gosms")


class _BaseClient:
    """Base class providing validation, URL building, and error parsing."""

    BASE_URL: str = "https://api.gosms.ge/api"

    def __init__(
        self,
        api_key: str,
        *,
        timeout: int = 30,
        retries: int = 1,
        debug: bool = False,
    ) -> None:
        if not api_key:
            raise TypeError("api_key is required")
        if not isinstance(api_key, str):
            raise TypeError("api_key must be a string")

        self._api_key = api_key
        self._timeout = timeout
        self._retries = max(1, retries)
        self._debug = debug

        if debug:
            logging.basicConfig(level=logging.DEBUG)

    def _build_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}/{endpoint}"

    def _build_payload(self, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {"api_key": self._api_key}
        payload.update(kwargs)
        return payload

    def _parse_response(
        self, data: dict[str, Any], status_code: int, headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        error_code = data.get("errorCode", 0)
        if status_code >= 400 or error_code:
            retry_after = None
            if headers:
                ra = headers.get("Retry-After")
                if ra:
                    retry_after = int(ra)
            raise GoSmsApiError(
                error_code=error_code,
                message=data.get("message", "Unknown error"),
                retry_after=retry_after,
            )
        return data

    def _validate_phone_number(self, value: Any, param_name: str) -> None:
        if not value or not isinstance(value, str):
            raise TypeError(f"{param_name} is required and must be a string")

    def _validate_string(self, value: Any, param_name: str) -> None:
        if not value or not isinstance(value, str):
            raise TypeError(f"{param_name} is required and must be a string")

    def _log(self, *args: Any) -> None:
        if self._debug:
            logger.debug("[GOSMS Debug] %s", " ".join(str(a) for a in args))

    def _calculate_delay(self, attempt: int) -> float:
        """Exponential backoff: 1s, 2s, 4s, ..."""
        return float(2 ** (attempt - 1))
