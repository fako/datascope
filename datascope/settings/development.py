from .base import *

DEBUG = True

INSTALLED_APPS += (
    # 'debug_toolbar',
    'django_extensions',
)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_COLLAPSED': True
}
DEBUG_TOOLBAR = True

#REQUESTS_PROXIES = REQUESTS_PROXIES_ENABLED
#REQUESTS_VERIFY = False

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

MAX_BATCH_SIZE = None  # better for sqlite to let Django determine batch size

# DATABASES["default"]["ENGINE"] = 'django.db.backends.mysql'
# DATABASES["default"]["NAME"] = 'datascope'
# DATABASES["default"]["USER"] = 'root'
# DATABASES["default"]["PASSWORD"] = ''
