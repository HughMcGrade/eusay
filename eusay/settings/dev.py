from .base import *


DEBUG = True
TEMPLATE_DEBUG = True

INSTALLED_APPS += ('debug_toolbar', )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'eusay',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
        'client_encoding': 'UTF8',
        'default_transaction_isolation': 'read committed',
        'timezone': 'Europe/London',
    }
}