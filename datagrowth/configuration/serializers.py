import argparse
import hashlib
from urllib.parse import parse_qsl

from .types import ConfigurationType


def load_config(defaults):
    """
    This decorator will turn the value of any keyword arguments named "config" into a ConfigurationType.
    The decorated function will get the configuration as its first argument.

    :param defaults: (dict) which should be used as default for inserted configuration.
    :return: ConfigurationType
    """

    def wrap(func):
        def config_func(*args, **kwargs):
            config = kwargs.pop("config", {})
            if not config:
                raise TypeError("load_config decorator expects a config kwarg.")
            if not isinstance(config, dict):
                return func(config, *args, **kwargs)
            config_instance = ConfigurationType.from_dict(config, defaults)
            return func(config_instance, *args, **kwargs)
        return config_func
    return wrap


class DecodeConfigAction(argparse.Action):
    """
    This class can be used as action for any argsparse command line option (like Django management command options).
    It will parse a URL like parameter string into a dictionary. This dictionary can then be used to initialize
    a configuration.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        values = dict(parse_qsl(values))
        setattr(namespace, self.dest, values)


def get_standardized_configuration(configuration, as_hash=True):
    """
    Given a configuration this function will return a string that represents that configuration.
    The representation is always the same for the same configuration.
    Default configurations are not taken into account and neither are protected and private configurations.
    Optionally this function can hash the representative string.

    :param configuration: (ConfigurationType) the configuration to represent
    :param as_hash: (bool) will return representation as a sha256 hash if True
    :return:
    """
    sorted_by_keys = sorted(configuration.items(), key=lambda item: item[0])
    standardized = "&".join("{}={}".format(key, value) for key, value in sorted_by_keys)
    if not as_hash:
        return standardized
    hasher = hashlib.sha256()
    hasher.update(bytes(standardized, encoding="utf-8"))
    return hasher.hexdigest()
