import requests

from gosms.sms import SMS
from gosms.settings import DEV_URLS, GOSMS_SETTINGS as SETTINGS
import requests_mock

try:
    from django.conf.settings import GOSMS_SETTINGS, DEBUG

    SETTINGS['dev_mode'] = DEBUG
    # override dev_mode in GOSMS_SETTINGS in order to use GoSMS.Ge api in development
    SETTINGS.update(GOSMS_SETTINGS)

except ModuleNotFoundError:
    """Create gosms manually and pass api_key"""
    pass

sms: SMS = SMS(SETTINGS['api_key'])
