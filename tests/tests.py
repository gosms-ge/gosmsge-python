import unittest
import requests_mock
from gosms.factories import SMSFactory
from gosms.settings import GOSMS_SETTINGS

from gosms.sms import SMS, ConsoleClient


@requests_mock.Mocker()
class SMSClassTest(unittest.TestCase):
    def setUp(self) -> None:
        GOSMS_SETTINGS['client'] = ConsoleClient

        self.sms = SMS('1111')
        self.sms_object: SMSFactory = SMSFactory()

    def test_send_message(self, m) -> None:
        response: dict = self.sms.client.send(self.sms_object.sender, self.sms_object.to, self.sms_object.text)

        def base_check():
            self.assertEqual(response.get('text'), self.sms_object.text)
            self.assertEqual(response.get('to'), self.sms_object.to)
            self.assertEqual(response.get('from'), self.sms_object.sender)
            self.assertEqual(response.get('success'), True)

        base_check()

        response: dict = self.sms.client.status(response['messageId'])
        base_check()
        self.assertEqual(response['status'], 'DELIVERED')

        response: dict = self.sms.client.send(self.sms_object.sender, f'{self.sms_object.to}5993', self.sms_object.text)

        self.assertEqual(response['success'], False)

    def test_otp(self, m) -> None:
        _response: dict = self.sms.client.send_otp(self.sms_object.to)
        self.assertEqual(_response.get('to'), self.sms_object.to)

        response: dict = self.sms.client.verify_otp(self.sms_object.to, _response['hash'], _response['code'])
        self.assertEqual(response.get('success'), True)
        self.assertEqual(response.get('verify'), True)

        response: dict = self.sms.client.verify_otp(self.sms_object.to, _response['hash'], _response['code'] - 1)
        self.assertEqual(response.get('success'), True)
        self.assertEqual(response.get('verify'), False)


if __name__ == '__main__':
    unittest.main()
