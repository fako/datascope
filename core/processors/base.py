from __future__ import unicode_literals, absolute_import, print_function, division

from core.utils.configuration import ConfigurationProperty
from datascope.configuration import DEFAULT_CONFIGURATION


class ArgumentsTypes:
    NORMAL = 'normal'
    BATCH = 'batch'


class Processor(object):

    DEFAULT_ARGS_TYPE = ArgumentsTypes.NORMAL
    ARGS_NORMAL_METHODS = []
    ARGS_BATCH_METHODS = []

    config = ConfigurationProperty(
            storage_attribute="_config",
            defaults=DEFAULT_CONFIGURATION,
            private=[],
            namespace='global'
    )

    def __init__(self, config):
        assert isinstance(config, dict), "Processor expects to always get a configuration."
        self.config = config

    def get_processor_method(self, method_name):
        if method_name in self.ARGS_NORMAL_METHODS:
            args_type = ArgumentsTypes.NORMAL
        elif method_name in self.ARGS_BATCH_METHODS:
            args_type = ArgumentsTypes.BATCH
        else:
            args_type = self.DEFAULT_ARGS_TYPE
        return getattr(self, method_name), args_type
