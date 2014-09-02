from .base import *

import appenlight_client.client as e_client


ENVIRONMENT = "production"

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS += ["eusay.eusa.ed.ac.uk",
                  ".eusay.eusa.ed.ac.uk"]  # Period matches any subdomains

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

# Make AppEnlight be the first value in MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES = \
    ('appenlight_client.django_middleware.AppenlightMiddleware',) + \
    MIDDLEWARE_CLASSES

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
)

APPENLIGHT = e_client.get_config(
    {'appenlight.api_key':get_secret("APPENLIGHT_PRIVATE_KEY")})