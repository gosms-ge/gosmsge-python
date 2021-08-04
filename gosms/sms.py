from gosms.exceptions import ApiError
from gosms.request import Request, MockRequest
from gosms.settings import GOSMS_SETTINGS, DEV_URLS


class SMS:
    urls = {
        'sms_send': 'https://api.gosms.ge/api/sendsms',
        'sms_check': 'https://api.gosms.ge/api/checksms',
        'otp_send': 'https://api.gosms.ge/api/otp/send',
        'otp_verify': 'https://api.gosms.ge/api/otp/verify',
        'balance_check': 'https://api.gosms.ge/api/sms-balance'
    }

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.request = Request()
        if GOSMS_SETTINGS['dev_mode']:
            SMS.urls = DEV_URLS
            self.request = MockRequest()

    def __post(self, url_key: str, data=None) -> dict:
        """ utility method for sending post requests """
        if data is None:
            data = dict()
        data['api_key'] = self.api_key
        response = self.request.post(
            SMS.urls[url_key],
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
