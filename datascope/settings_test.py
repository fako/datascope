from .settings_base import *


DATASCOPE_VERSION = "0.0.0"
MAX_BATCH_SIZE = None  # better for sqlite to let Django determine batch size
STATIC_IP = "127.0.0.1"
USE_MOCKS = True

LOGGING["loggers"] = {}

MIGRATION_MODULES = {
    'auth': None,
    'contenttypes': None,
    'default': None,
    'sessions': None,

    'datascope': None,
    'core': None,
    'sources': None,
    'wiki_feed': None,
    'visual_translations': None,
    'future_fashion': None,
    'open_data': None,
    'wiki_scope': None,
    'online_discourse': None,
    'nautilus': None,
    'setup_utrecht': None,
}
