from datetime import timedelta


BROKER_URL = 'redis://localhost:6379/0'

CELERYBEAT_SCHEDULE = {
    'update-ranks-every-5-minutes': {
        'task': 'eusay.tasks.update_proposal_ranks',
        'schedule': timedelta(minutes=5)
    },
}
CELERY_TIMEZONE = 'Europe/London'

# Names of nodes to start
#   most will only start one node:
CELERYD_NODES="worker1"
#   but you can also start multiple and configure settings
#   for each in CELERYD_OPTS (see `celery multi --help` for examples).

# Absolute or relative path to the 'celery' command:
# TODO: don't hardcode
CELERY_BIN="/home/admin/.virtualenvs/eusay/bin/celery"
#CELERY_BIN="/virtualenvs/def/bin/celery"

# App instance to use
# comment out this line if you don't use an app
CELERY_APP="eusay"
# or fully qualified:
#CELERY_APP="proj.tasks:app"

# Where to chdir at start.
# TODO: don't hardcode
CELERYD_CHDIR="/home/admin/public_html/eusay/"

# Extra command-line arguments to the worker
# CELERYD_OPTS="--time-limit=300 --concurrency=8"

# %N will be replaced with the first part of the nodename.
CELERYD_LOG_FILE="/var/log/celery/%N.log"
CELERYD_PID_FILE="/var/run/celery/%N.pid"

# Workers should run as an unprivileged user.
#   You need to create this user manually (or you can choose
#   a user/group combination that already exists, e.g. nobody).
CELERYD_USER="celery"
CELERYD_GROUP="celery"

# If enabled pid and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1