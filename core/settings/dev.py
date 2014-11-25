from .base import *

ENVIRONMENT = "dev"

DEBUG = True
TEMPLATE_DEBUG = True

INSTALLED_APPS += ('debug_toolbar', )

ALLOWED_HOSTS += ["127.0.0.1", "localhost"]

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

# set these to the empty string in development so we don't track these sessions
PRIVATE_GOOGLE_ANALYTICS_KEY = ""
EUSA_GOOGLE_ANALYTICS_KEY = ""
