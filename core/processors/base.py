from __future__ import unicode_literals, absolute_import, print_function, division

from core.utils.configuration import ConfigurationProperty
from datascope.configuration import DEFAULT_CONFIGURATION


class Processor(object):

    DEFAULT_RETURN_TYPE = list
    RETURN_LIST_METHODS = []
    RETURN_DICT_METHODS = []

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
        pass
