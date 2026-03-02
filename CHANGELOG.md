# Changelog

All notable changes to the GoSMS.GE Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-02-27

### Added

- **OTP Rate Limit Headers**: `send_otp()` and `verify_otp()` now return rate limit information via the `rate_limit` field on `OtpSendResponse` and `OtpVerifyResponse`.
- **`RateLimitInfo` dataclass**: New type with `limit`, `remaining`, and `retry_after` fields, extracted from `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After` response headers.
- **`retry_after` on `GoSmsApiError`**: When the API returns error codes `109` (TOO_MANY_REQUESTS) or `110` (ACCOUNT_LOCKED), the `retry_after` attribute contains the lockout duration in seconds.
- **`RateLimitInfo` exported** from the top-level `gosms` package.

### Changed

- `_make_request()` now returns both response data and headers (internal change, no public API impact).
- `_parse_response()` now accepts optional headers to extract `Retry-After` for error responses.

## [2.0.0] - 2025-01-15

### Changed

- Complete rewrite of the SDK.
- Explicit client instantiation (`SMS("api_key")`) instead of module-level singleton.
- `GoSmsApiError` extends `Exception` (was `BaseException`).
- All responses are typed frozen dataclasses.
- Django integration uses lazy factory (`get_sms_client()`).
- Removed `dev_mode` / `RequestMock` in favor of standard test mocking.

### Added

- Async client (`AsyncSMS`) via `pip install gosms-python[async]`.
- `GoSmsErrorCode` constants for typed error handling.
- `send_bulk()` and `create_sender()` endpoints.
- Configurable `timeout` and `retries` with exponential backoff.
- Debug logging via `debug=True`.
