from gosms.sms import SMS
from gosms.settings import GOSMS_SETTINGS as SETTINGS

try:
    from django.conf.settings import GOSMS_SETTINGS, DEBUG

    SETTINGS['dev_mode'] = DEBUG
    # override dev_mode in GOSMS_SETTINGS in order to use GoSMS.Ge api in development
    SETTINGS.update(GOSMS_SETTINGS)

except ModuleNotFoundError:
    """Create gosms manually and pass api_key"""
    pass

if SETTINGS['dev_mode']:
    SETTINGS['client'] = 'gosms.sms.ConsoleClient'

client = getattr(__import__('gosms.sms', fromlist=['GOSMSClient']), 'GOSMSClient')

sms: SMS = SMS(SETTINGS['api_key'], client=client)
