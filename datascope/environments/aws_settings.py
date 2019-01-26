from datascope.settings_base import *

DATABASES["default"]["ENGINE"] = 'django.db.backends.mysql'
DATABASES["default"]["NAME"] = 'datascope'
DATABASES["default"]["USER"] = 'django'
DATABASES["default"]["PASSWORD"] = MYSQL_PASSWORD

STATIC_IP = "34.251.167.142"

RAVEN_CONFIG = {
    'dsn': RAVEN_DSN,
    'release': DATASCOPE_VERSION,
    'site': '34.251.167.142'
}

# This disables sessions for other than admin
# CSRF problems with rest_framework need to be solved
# Before we can allow sessions on /data
SESSION_COOKIE_PATH = "/admin"

DATAGROWTH_DATA_DIR = os.path.join(os.sep, "srv", "data")
DATAGROWTH_MEDIA_ROOT = MEDIA_ROOT = os.path.join(DATAGROWTH_DATA_DIR, "media")
DATAGROWTH_BIN_DIR = os.path.join(os.sep, "srv", "bin")
