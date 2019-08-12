from celery.schedules import crontab
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from datascope.settings_base import *


STATIC_IP = "37.139.10.19"

CELERY_BEAT_SCHEDULE = {
    "grow_locafora": {
        "task": "nautilus.grow_locafora",
        "schedule": crontab(minute=0, hour=23, day_of_week=4),
    },
    "clear_locafora": {
        "task": "nautilus.clear_locafora",
        "schedule": crontab(minute=0, hour=23, day_of_week=6),
    }
}

# Sentry error reporting
sentry_sdk.init(
    dsn="https://407d0ac6dc4542c9a60fb299e32e464d@sentry.io/241870",
    integrations=[DjangoIntegration()],
    release=DATASCOPE_VERSION,
    server_name='data-scope.com'
)

DATAGROWTH_DATA_DIR = os.path.join(os.sep, "srv", "data")
DATAGROWTH_MEDIA_ROOT = MEDIA_ROOT = os.path.join(DATAGROWTH_DATA_DIR, "media")
DATAGROWTH_BIN_DIR = os.path.join(os.sep, "srv", "bin")
