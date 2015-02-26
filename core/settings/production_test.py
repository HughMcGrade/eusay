from .base import *

ENVIRONMENT = "production"

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'eusay',
        'USER': 'eusay',
        'PASSWORD': get_secret("POSTGRES_PASSWORD"),
        'HOST': 'localhost',
        'PORT': '',
        'client_encoding': 'UTF8',
        'default_transaction_isolation': 'read committed',
        'timezone': 'Europe/London',
    }
}

ALLOWED_HOSTS += ["127.0.0.1", "localhost"]