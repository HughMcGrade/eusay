from .base import *


ENVIRONMENT = "production"

DEBUG = False
TEMPLATE_DEBUG = False

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

MIDDLEWARE_CLASSES += (
    'django.contrib.auth.middleware.RemoteUserMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
)
