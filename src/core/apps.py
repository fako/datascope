import logging
from django.apps import AppConfig

from datagrowth.configuration import register_defaults


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        register_defaults("global", {
            "resource_exception_log_level": logging.WARNING
        })
