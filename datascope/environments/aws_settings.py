import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from datascope.settings_base import *

DATABASES["default"]["NAME"] = 'datascope'
DATABASES["default"]["USER"] = 'django'
DATABASES["default"]["PASSWORD"] = DATABASE_PASSWORD

STATIC_IP = "34.251.167.142"

# Sentry error reporting
sentry_sdk.init(
    dsn="https://8402764df7cc487b93b15cf2163c456f@sentry.io/1277824",
    integrations=[DjangoIntegration()],
    release=DATASCOPE_VERSION,
    server_name='data-scope.com'
)

# This disables sessions for other than admin
# CSRF problems with rest_framework need to be solved
# Before we can allow sessions on /data
SESSION_COOKIE_PATH = "/admin"

DATAGROWTH_DATA_DIR = os.path.join(os.sep, "srv", "data")
DATAGROWTH_MEDIA_ROOT = MEDIA_ROOT = os.path.join(DATAGROWTH_DATA_DIR, "media")
DATAGROWTH_BIN_DIR = os.path.join(os.sep, "srv", "bin")
