# GoSMS.GE Python SDK

[![PyPI version](https://img.shields.io/pypi/v/gosms-python.svg)](https://pypi.org/project/gosms-python/)
[![Python versions](https://img.shields.io/pypi/pyversions/gosms-python.svg)](https://pypi.org/project/gosms-python/)
[![Tests](https://github.com/gosms-ge/gosmsge-python/actions/workflows/release.yml/badge.svg)](https://github.com/gosms-ge/gosmsge-python/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for the [GoSMS.GE](https://gosms.ge) SMS gateway. Send SMS messages, manage OTP verification, and check balances with both sync and async clients.

## Installation

```bash
pip install gosms-python
```

For async support:

```bash
pip install gosms-python[async]
```

## Quick Start

```python
from gosms import SMS

sms = SMS("your_api_key")

# Send a message
result = sms.send("995555123456", "Hello!", "GOSMS.GE")
print(result.message_id)  # 12345
print(result.balance)     # 99

# Check balance
balance = sms.balance()
print(balance.balance)  # 500
```

## All Endpoints

### Send SMS

```python
result = sms.send("995555123456", "Hello!", "GOSMS.GE")
result = sms.send("995555123456", "Urgent!", "GOSMS.GE", urgent=True)
```

### Send Bulk SMS

```python
result = sms.send_bulk(
    "GOSMS.GE",
    ["995555111111", "995555222222"],
    "Hello everyone!",
)
print(result.total_count)    # 2
print(result.success_count)  # 2

for msg in result.messages:
    print(f"{msg.to}: {msg.message_id}")
```

### Send OTP

```python
result = sms.send_otp("995555123456")
print(result.hash)  # "abc123hash" — save this for verification
```

### Verify OTP

```python
result = sms.verify_otp("995555123456", "abc123hash", "1234")
print(result.verify)  # True
```

### Check Message Status

```python
result = sms.status(12345)
print(result.status)  # "delivered"
```

### Check Balance

```python
result = sms.balance()
print(result.balance)  # 500
```

### Create Sender Name

```python
result = sms.create_sender("MyBrand")
print(result.success)  # True
```

## Async Usage

```python
import asyncio
from gosms import AsyncSMS

async def main():
    async with AsyncSMS("your_api_key") as sms:
        result = await sms.send("995555123456", "Hello!", "GOSMS.GE")
        print(result.message_id)

        balance = await sms.balance()
        print(balance.balance)

asyncio.run(main())
```

All methods from the sync client are available as async equivalents with the same signatures.

## Django Integration

Add to your `settings.py`:

```python
GOSMS_SETTINGS = {
    "api_key": "your_api_key",
    "timeout": 30,    # optional
    "retries": 1,     # optional
}
```

Use anywhere in your project:

```python
from gosms.django import get_sms_client

sms = get_sms_client()
sms.send("995555123456", "Hello!", "GOSMS.GE")
```

The client is created lazily on first call and reused as a singleton.

## Configuration

```python
sms = SMS(
    "your_api_key",
    timeout=30,   # request timeout in seconds (default: 30)
    retries=3,    # retry attempts on failure (default: 1)
    debug=True,   # enable debug logging (default: False)
)
```

## Error Handling

```python
from gosms import SMS, GoSmsApiError, GoSmsErrorCode

sms = SMS("your_api_key")

try:
    result = sms.send("995555123456", "Hello!", "GOSMS.GE")
except GoSmsApiError as e:
    print(e.error_code)  # 100
    print(e.message)     # "Invalid API key"

    if e.error_code == GoSmsErrorCode.INVALID_API_KEY:
        print("Check your API key")
```

### Error Codes

| Code | Constant | Description |
|------|----------|-------------|
| 100 | `INVALID_API_KEY` | Invalid API key |
| 101 | `INVALID_PHONE_NUMBER` | Invalid phone number |
| 102 | `INSUFFICIENT_BALANCE` | Insufficient balance |
| 103 | `SENDER_NOT_FOUND` | Sender name not found |
| 104 | `INVALID_TEXT` | Invalid message text |
| 105 | `TOO_MANY_RECIPIENTS` | Too many recipients (max 1000) |
| 106 | `INVALID_MESSAGE_ID` | Invalid message ID |
| 107 | `SENDER_EXISTS` | Sender name already exists |
| 108 | `INVALID_SENDER_NAME` | Invalid sender name |
| 109 | `INVALID_OTP_HASH` | Invalid OTP hash |
| 110 | `INVALID_OTP_CODE` | Invalid OTP code |
| 111 | `OTP_EXPIRED` | OTP expired |
| 112 | `OTP_ALREADY_VERIFIED` | OTP already verified |
| 113 | `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |

## Response Types

All methods return typed frozen dataclasses:

| Method | Return Type | Key Fields |
|--------|-------------|------------|
| `send()` | `SmsSendResponse` | `success`, `message_id`, `balance` |
| `send_bulk()` | `SendBulkSmsResponse` | `success`, `total_count`, `messages` |
| `send_otp()` | `OtpSendResponse` | `success`, `hash`, `balance` |
| `verify_otp()` | `OtpVerifyResponse` | `success`, `verify` |
| `status()` | `CheckStatusResponse` | `success`, `status`, `message_id` |
| `balance()` | `BalanceResponse` | `success`, `balance` |
| `create_sender()` | `SenderCreateResponse` | `success` |

## Migration from v1.x

v2.0 is a complete rewrite. Key changes:

```python
# v1.x (old)
from gosms import sms                    # module-level singleton
sms.send('995...', 'text', 'SENDER')

# v2.0 (new)
from gosms import SMS                    # explicit instantiation
sms = SMS('your_api_key')
sms.send('995...', 'text', 'SENDER')

# v1.x Django (old)
from gosms import sms                    # import-time side effect

# v2.0 Django (new)
from gosms.django import get_sms_client  # lazy factory
sms = get_sms_client()
```

Other changes:
- `GoSmsApiError` now extends `Exception` (was `BaseException`)
- Added `GoSmsErrorCode` constants for typed error handling
- Added `send_bulk()` and `create_sender()` endpoints
- Added async client (`AsyncSMS`) via `pip install gosms-python[async]`
- All responses are typed frozen dataclasses
- Removed `dev_mode` / `RequestMock` in favor of standard test mocking

## License

MIT

## Links

- Website: https://gosms.ge
- PyPI: https://pypi.org/project/gosms-python/
- GitHub: https://github.com/gosms-ge/gosmsge-python
- Support: info@gosms.ge
