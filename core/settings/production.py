from .base import *


ENVIRONMENT = "production"

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS += ["129.215.116.90",
                  "eusay.eusa.ed.ac.uk",
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

MIDDLEWARE_CLASSES += ('django.contrib.auth.middleware.RemoteUserMiddleware',)

AUTHENTICATION_BACKENDS = (
    'core.auth_backend.CustomUserModelBackend',
)

ADMINS = (("Hugh", "hugh_mcgrade@hotmail.co.uk"), ("Tao", "tao@btao.org"))
