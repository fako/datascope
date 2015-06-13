from base import *

DATABASES["default"]["ENGINE"] = 'django.db.backends.mysql'
DATABASES["default"]["NAME"] = 's52573__datascope'
DATABASES["default"]["USER"] = 's52573'
DATABASES["default"]["PASSWORD"] = WIKILABS_MYSQL_PASSWORD
DATABASES["default"]["HOST"] = 'tools-db'
