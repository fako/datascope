from celery.schedules import crontab

from datascope.settings_base import *

DATABASES["default"]["ENGINE"] = "django.db.backends.mysql"
DATABASES["default"]["NAME"] = "s52573__datascope"
DATABASES["default"]["USER"] = "s52573"
DATABASES["default"]["PASSWORD"] = MYSQL_PASSWORD
DATABASES["default"]["HOST"] = "tools-db"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
STATIC_URL = "//tools-static.wmflabs.org/algo-news/static/"

CELERY_DEFAULT_QUEUE = "datascope"
CELERY_BROKER_URL = "redis://tools-redis:6379/0"
CELERY_BEAT_SCHEDULE = {
    "update_wiki_feed": {
        "task": "wiki_feed.update_wiki_feed",
        "schedule": crontab(minute=0, hour=6),
    }
}

MAX_BATCH_SIZE = 100

RAVEN_CONFIG = {
    "dsn": RAVEN_DSN,
    "release": DATASCOPE_VERSION,
    "site": "tools.wmflabs.org"
}

# TODO: add STATIC_IP
