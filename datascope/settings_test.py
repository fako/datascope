from .settings_base import *


DATASCOPE_VERSION = "0.0.0"
MAX_BATCH_SIZE = None  # better for sqlite to let Django determine batch size
STATIC_IP = "127.0.0.1"

LOGGING["loggers"] = {}


class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


MIGRATION_MODULES = DisableMigrations()
