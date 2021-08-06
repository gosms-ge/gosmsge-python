# GOSMS.GE Python SMS Send

Python client module to send SMS messages using GOSMS.GE SMS Gateway.

To use this library, you must have a valid account on https://gosms.ge.

**Please note** SMS messages sent with this library will be deducted by your GOSMS.GE account credits.

For any questions, please contact: info@gosms.ge

# usage

### Send a message with Classic type

```python
from gosms import SMS

sms: SMS = SMS('api_key')

sms.send('995555555555', 'Hello!', 'GOSMS.GE')
```

### Check status of message

```python
from gosms import SMS

sms: SMS = SMS('api_key')

sms.status('message_id')
```

### Check balance

```python
from gosms.settings import GOSMS_SETTINGS
from gosms import sms

GOSMS_SETTINGS['api_key'] = 'your_api_key'

sms.balance()
```

# usage in Django

```python
# django settings file

GOSMS_SETTINGS = {
    # you should have valid API key given by gosms.ge
    'api_key': 'your_api_key',

    # this property will have same value as DEBUG but you can override it here
    'dev_mode': False,
}
```

```python
# views.py
from gosms import sms


def send_message_view(request):
    """ :returns {"code": string,"message": string,"message_id": number,"balance": number,"user": string} """
    return sms.send('995555555555', 'Hello!', 'GOSMS.GE')


def check_status_view(request):
    """ :returns { id: number,sender: string,receiver: string,message: string',message_id: string,amount: number,status: string } """
    return sms.status('message_id')


def check_balance_view(request):
    """ returns { balance: number, user: string } """
    return sms.balance()
```

### You can use it anywhere

```python
# user.managers
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not phone_number:
            raise ValueError('The given phone_number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)
```

```python
# user.models
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

from user.managers import UserManager

from gosms import sms


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(_('Phone Number'), unique=True)
    is_active = models.BooleanField(_('Is Active'), default=False)
    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        sms.send(self.phone_number, 'user created', 'GOSMS.GE')
```

```python
# views.py
from django.shortcuts import get_object_or_404, render

from user.models import User
from gosms import sms


def user_register(request):
    user = User(
        phone_number=request.POST.get('phone_number'),
    )
    user.set_password(request.POST.get('password'))
    user.save()
    sms.send_otp(user.phone_number)


def verify_user(request):
    """ verify otp method raises exception if details are incorrect """
    response_data = sms.verify_otp(
        request.POST.get('phone_number'),
        request.POST.get('hash'),
        request.POST.get('code')
    )

    user = get_object_or_404(
        User, phone_number=request.POST.get('phone_number')
    )
    user.is_active = True
    user.save()
    return render(request, 'some_template', context=response_data)
```

## More info

You can check out our website https://www.gosms.ge

