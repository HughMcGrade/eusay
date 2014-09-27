# Required for django-endless-pagination plugin
# http://django-endless-pagination.readthedocs.org
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

import json
import os


BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname((__file__)))))

# JSON-based secrets module
with open(os.path.join(BASE_DIR, "secrets.json")) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    """Get the secret variable or return explicit exception."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Add {0} to your secrets file.".format(setting)
        raise ImproperlyConfigured(error_msg)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret("SECRET_KEY")

MANDRILL_API_KEY = get_secret("MANDRILL_API_KEY")
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
SERVER_EMAIL = "eusay@btao.org"  # TODO: use @eusay.eusa.ed.ac.uk address

AUTH_USER_MODEL = 'users.User'

# Required for django-endless-pagination plugin
# http://django-endless-pagination.readthedocs.org
TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATE_DIRS = tuple(os.path.join(BASE_DIR, "core/templates"))

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'bootstrap_admin',  # Added
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'core',
    'comments',
    'proposals',
    'votes',
    'moderation',
    'tags',
    'api_v1',
    'search',
    'core.settings',
    'notifications',
    'student_councils',

    # Added
    'endless_pagination',
    'rest_framework',
    'haystack',
    'core.templatetags',
    'djrill'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny', # TODO: permissions for API access. for now, allow any
    )
}


# Search
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
"""
Using a realtime signal processor means that the search index is updated every
time a proposal is added or deleted. Since eusay is small, this should be
fine - but if we have performance issues, we can use BaseSignalProcessor and
manually run a cron job to rebuild the index every few hours or something.
"""

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = 'static/'


# For boostrap alerts
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
