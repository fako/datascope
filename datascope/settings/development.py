from base import *

DEBUG = True

# INSTALLED_APPS += (
#     'debug_toolbar',
#     'django_extensions',
# )

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_COLLAPSED': True
}
DEBUG_TOOLBAR = True

#REQUESTS_PROXIES = REQUESTS_PROXIES_ENABLED
REQUESTS_VERIFY = False

# MIDDLEWARE_CLASSES += (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# )