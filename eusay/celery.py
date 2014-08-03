import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eusay.settings')

celery = Celery('eusay',
                include=['eusay.tasks'])

# Using a string here means the worker will not have to
# pickle the object when using Windows.
celery.config_from_object('celeryconfig')
celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@celery.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))