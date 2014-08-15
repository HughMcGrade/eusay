from .base import *


DEBUG = False
TEMPLATE_DEBUG = False

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

# TODO: test these!
MIDDLEWARE_CLASSES += (
    'django.contrib.auth.middleware.RemoteUserMiddleware'
)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
)