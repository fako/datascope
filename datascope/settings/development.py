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


STATIC_IP = "127.0.0.1"
#STATIC_IP = "172.24.1.97"
#MEDIA_URL = 'http://' + STATIC_IP + ':8080/media/'
#STATIC_URL = 'http://' + STATIC_IP + ':8080/static/'
