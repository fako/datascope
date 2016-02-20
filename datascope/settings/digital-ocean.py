from base import *

DATABASES["default"]["ENGINE"] = 'django.db.backends.mysql'
DATABASES["default"]["NAME"] = 'datascope'
DATABASES["default"]["USER"] = 'django'
DATABASES["default"]["PASSWORD"] = MYSQL_PASSWORD