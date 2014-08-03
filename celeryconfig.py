from datetime import timedelta


BROKER_URL = 'redis://localhost:6379/0'

CELERYBEAT_SCHEDULE = {
    'update-ranks-every-5-minutes': {
        'task': 'eusay.tasks.update_proposal_ranks',
        'schedule': timedelta(minutes=10)
    },
}
CELERY_TIMEZONE = 'Europe/London'