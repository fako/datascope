import importlib
import inspect

from django.apps import AppConfig, apps


class CoreConfig(AppConfig):

    name = "core"
    processors = {}

    def ready(self):
        self.load_processors()

    def load_processors(self):
        from core.processors.base import Processor
        self.processors = {}
        for app_config in apps.get_app_configs():
            try:
                processor_module = importlib.import_module(app_config.module.__name__ + ".processors")
                for name, attr in processor_module.__dict__.items():
                    if name in self.processors:
                        raise RuntimeError("The {} Processor is being loaded twice".format(name))
                    if inspect.isclass(attr) and issubclass(attr, Processor):
                        self.processors[name] = attr
            except ImportError:
                continue

    def get_processor_class(self, name):
        return self.processors.get(name, None)
