import re
from datetime import datetime
import random
from urllib.parse import parse_qs

import requests

from abc import ABC, abstractmethod
import requests_mock.request
from requests import Response


class Validation:
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        reg = re.compile('^(995)[\d]{9}')
        if phone[:3] != '995':
            phone = f'995P{phone}'

        return True if reg.fullmatch(phone) else False


class AbstractRequest(ABC):
    @abstractmethod
    def post(self, url: str, **kwargs) -> Response:
        """ post method to send POST requests to specific urls """

    @abstractmethod
    def get(self, url: str, **kwargs) -> Response:
        """ get method to send GET requests to specific urls """


class MockRequest(AbstractRequest, Validation):
    message_id: int = 0
    balance: int = 94

    def __init__(self) -> None:
        self.adapter = requests_mock.Adapter()
        self.session = requests.session()

        self.__init_uris()
        self.session.mount('mock://', self.adapter)

        self._messages = {}
        self._otp = {}

    @staticmethod
    def parse_request_data(data) -> dict:
        return parse_qs(data, keep_blank_values=True)

    def __get_message(self, message_id) -> dict:
        return self._messages[int(message_id)]

    def __sms_send(self, request, context) -> dict:
        data = MockRequest.parse_request_data(request.text)

        if MockRequest.validate_phone_number(data.get('to')[0]):
            MockRequest.message_id += 1
            message_data = {
                'success': True,
                'messageId': MockRequest.message_id,
                'from': data.get('from')[0],
                'to': data.get('to')[0],
                'text': data.get('text')[0],
                'sendAt': datetime.now().isoformat(),
                'balance': MockRequest.balance,
                'encode': "unicode",
                'segment': 1,
                'smsCharacters': len(data.get('text')[0])
            }
            self._messages[MockRequest.message_id] = message_data

            return message_data

        return {
            'success': False
        }

    def __sms_check(self, request, context) -> dict:
        data = MockRequest.parse_request_data(request.text)
        message_data = {
            'status': 'DELIVERED',
            **self.__get_message(data.get('messageId')[0])
        }
        return message_data

    @staticmethod
    def __balance_check() -> dict:
        return {
            'success': True,
            'balance': MockRequest.balance
        }

    def __send_otp(self, request, context) -> dict:
        data = MockRequest.parse_request_data(request.text)
        phone = data.get('phone')[0]
        if MockRequest.validate_phone_number(phone):
            hash_key = ''.join([chr(random.randint(97, 122)) for _ in range(30)])
            code = int(''.join([str(random.randint(0, 9)) for _ in range(4)]))

            self._otp[phone] = {
                'hash': hash_key,
                'code': code
            }

            return {
                'success': True,
                'hash': hash_key,
                'code': code,
                'to': phone,
                'sendAt': datetime.now().isoformat(),
                'encode': "default",
                'segment': 1,
                'smsCharacters': 57
            }
        else:
            return {
                'success': False
            }

    def __verify_otp(self, request, context) -> dict:
        data = MockRequest.parse_request_data(request.text)
        phone = data.get('phone')[0]
        hash_code = data.get('hash')[0]
        code = int(data.get('code')[0])

        if self._otp.get(phone):
            return {
                'success': True,
                'verify': self._otp[phone]['hash'] == hash_code and self._otp[phone]['code'] == code
            }
        else:
            return {
                'success': False,
                'verify': False
            }

    def __register_uri(self, *args, **kwargs) -> None:
        self.adapter.register_uri(*args, **kwargs)

    def __init_uris(self) -> None:
        from gosms import DEV_URLS

        self.__register_uri('POST', DEV_URLS['sms_send'], json=self.__sms_send)
        self.__register_uri('POST', DEV_URLS['sms_check'], json=self.__sms_check)
        self.__register_uri('POST', DEV_URLS['balance_check'], json=self.__balance_check)
        self.__register_uri('POST', DEV_URLS['otp_send'], json=self.__send_otp)
        self.__register_uri('POST', DEV_URLS['otp_verify'], json=self.__verify_otp)

    def post(self, url: str, **kwargs) -> Response:
        return self.session.post(url, **kwargs)

    def get(self, url: str, **kwargs) -> Response:
        return self.session.get(url, **kwargs)


class Request(AbstractRequest):
    def post(self, url: str, **kwargs) -> Response:
        return requests.post(url, **kwargs)

    def get(self, url: str, **kwargs) -> Response:
        return requests.get(url, **kwargs)
