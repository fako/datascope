from datascope.settings_base import *

DATABASES["default"]["ENGINE"] = 'django.db.backends.mysql'
DATABASES["default"]["NAME"] = 'datascope'
DATABASES["default"]["USER"] = 'django'
DATABASES["default"]["PASSWORD"] = MYSQL_PASSWORD

STATIC_IP = "37.139.10.19"

RAVEN_CONFIG = {
    'dsn': RAVEN_DSN,
    'release': DATASCOPE_VERSION,
    'site': 'data-scope.com'
}
