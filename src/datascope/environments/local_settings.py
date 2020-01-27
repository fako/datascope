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

#DATAGROWTH_REQUESTS_PROXIES = {
#    "http": "localhost:8888"
#}
#DATAGROWTH_REQUESTS_VERIFY = False

STATIC_IP = "127.0.0.1"
ALLOWED_HOSTS = ["*"]

ADMINS = (
    ('Administrator', 'administrator@example.com'),
)

MANAGERS = (
    ('Manager', 'manager@example.com'),
)

SERVER_EMAIL = 'server@example.com'
