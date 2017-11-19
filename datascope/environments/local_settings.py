from .settings_base import *

DEBUG = True
USE_MOCKS = True

INSTALLED_APPS += (
    'debug_toolbar',
    #'django_extensions',
)

DEBUG_TOOLBAR = True
INTERNAL_IPS = [
    "127.0.0.1"
]
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_COLLAPSED': True
}
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

#REQUESTS_PROXIES = REQUESTS_PROXIES_ENABLED
#REQUESTS_VERIFY = False

STATIC_IP = "127.0.0.1"
ALLOWED_HOSTS = ["*"]
