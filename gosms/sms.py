import random
from abc import ABC, abstractmethod
from datetime import datetime
import re

from gosms.exceptions import ApiError
import requests
from gosms.settings import GOSMS_SETTINGS


class Validation:
    @classmethod
    def validate_phone_number(cls, phone: str) -> bool:
        reg = re.compile('^(995)[\d]{9}')
        if phone[:3] != '995':
            phone = f'995P{phone}'

        return True if reg.fullmatch(phone) else False


class Client(ABC, Validation):
    @abstractmethod
    def send(self, sender: str, to: str, text: str) -> dict:
        """ gosms.ge sendsms method to send custom text to clients """

    @abstractmethod
    def status(self, message_id: str) -> dict:
        """ gosms.ge checksms method to check sms details """

    @abstractmethod
    def balance(self) -> dict:
        """ gosms.ge sms-balance method to check senders' remaining number or sms """

    @abstractmethod
    def send_otp(self, phone: str) -> dict:
        """ gosms.ge otp-send method to send one time passcode to clients """

    @abstractmethod
    def verify_otp(self, phone: str, hash_code: str, code: int) -> dict:
        """ gosms.ge otp-verify method to check correctness of client sent details """


class ConsoleClient(Client):
    message_id: int = 1
    _balance: int = 100

    def __init__(self, *args):
        self._otp = dict()
        self._data = dict()

    @classmethod
    def update_message_id(cls) -> int:
        message_id: int = cls.message_id
        cls.message_id += 1
        return message_id

    def status(self, message_id: str) -> dict:
        return {**self._data[message_id], 'status': 'DELIVERED'}

    def send(self, sender: str, to: str, text: str) -> dict:
        if ConsoleClient.validate_phone_number(to):
            self._data[ConsoleClient.message_id] = {
                "success": True,
                "messageId": ConsoleClient.message_id,
                "from": sender,
                "to": to,
                "text": text,
                "sendAt": datetime.now(),
                "balance": self._balance,
                "encode": "unicode",
                "segment": 1,
                "smsCharacters": len(text)
            }
            return self._data[ConsoleClient.update_message_id()]
        else:
            return {
                'success': False
            }

    def balance(self) -> dict:
        return {
            'success': True,
            'balance': self._balance
        }

    def verify_otp(self, phone: str, hash_code: str, code: int) -> dict:
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

    def send_otp(self, phone: str) -> dict:
        if ConsoleClient.validate_phone_number(phone):
            hash_key = hash(''.join([chr(random.randint(97, 122)) for _ in range(30)]))
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
                'sendAt': datetime.now(),
                'encode': "default",
                'segment': 1,
                'smsCharacters': 57
            }
        else:
            return {
                'success': False
            }


class GOSMSClient(Client):
    urls = {
        'sms_send': 'https://api.gosms.ge/api/sendsms',
        'sms_check': 'https://api.gosms.ge/api/checksms',
        'otp_send': 'https://api.gosms.ge/api/otp/send',
        'otp_verify': 'https://api.gosms.ge/api/otp/verify',
        'balance_check': 'https://api.gosms.ge/api/sms-balance'
    }

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def __post(self, url_key: str, data=None) -> dict:
        """ utility method for sending post requests """
        if data is None:
            data = dict()
        data['api_key'] = self.api_key
        response = requests.post(
            self.urls[url_key],
            data=data
        )
        response_data: dict = response.json()
        if response_data.get('errorCode'):
            raise ApiError(response_data)
        return response_data

    def send(self, sender: str, to: str, text: str) -> dict:
        """ gosms.ge sendsms method to send custom text to clients """
        return self.__post(
            'sms_send',
            {
                'from': sender,
                'to': to,
                'text': text
            }
        )

    def status(self, message_id: str) -> dict:
        """ gosms.ge checksms method to check sms details """
        return self.__post(
            'sms_check',
            {
                'messageId': message_id
            }
        )

    def balance(self) -> dict:
        """ gosms.ge sms-balance method to check senders' remaining number or sms """
        return self.__post(
            'balance_check'
        )

    def send_otp(self, phone: str) -> dict:
        """ gosms.ge otp-send method to send one time passcode to clients """
        return self.__post(
            'otp_send',
            {
                'phone': phone
            }
        )

    def verify_otp(self, phone: str, hash_code: str, code: int) -> dict:
        """ gosms.ge otp-verify method to check correctness of client sent details """
        return self.__post(
            'otp_verify',
            {
                'phone': phone,
                'hash': hash_code,
                'code': code
            }
        )


class SMS:
    # based on users setting
    # create appropriate instance
    def __init__(self, api_key, *, client: Client = None):
        if not client:
            client = GOSMS_SETTINGS['client']
        self.client = client(api_key)
