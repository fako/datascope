import warnings
from copy import copy

from datagrowth.settings import DATAGROWTH_DEFAULT_CONFIGURATION


class ConfigurationNotFoundError(AttributeError):
    pass


class ConfigurationType(object):
    """
    This type is the interface to configurations. Configurations are accessible as attributes.
    So a configuration named `my_config` will be accessible with `config.my_config`.

    You can check if a configuration exists by using the `in` operator.

    :param defaults: (dict) that should hold default configurations as items
        or None to load defaults from settings at runtime
    :param namespace: (string) prefix to search default configurations with
    :param private: (list) keys that are considered as private
    :return: ConfigurationType
    """

    _private_defaults = ["_private", "_defaults", "_namespace"]
    _global_prefix = "global"

    def __init__(self, defaults=None, namespace="global", private=("_private", "_defaults", "_namespace",)):
        """
        Initiates the ConfigurationType by checking arguments and setting logically private attributes

        :param defaults: (dict) that should hold default configurations as items
            or None to load defaults from settings at runtime
        :param namespace: (string) prefix to search default configurations with
        :param private: (list) keys that are considered as private
        :return: None
        """
        assert isinstance(defaults, dict) or defaults is None, \
            "Defaults should be a dict which values are the configuration defaults or None."
        assert isinstance(namespace, str), \
            "Namespaces should be a string that acts as a prefix for finding configurations."
        assert isinstance(private, (list, tuple,)), \
            "Private should be a list or tuple of private configurations."

        super(ConfigurationType, self).__init__()
        self._defaults = defaults
        self._namespace = namespace
        self._private = copy(self._private_defaults)
        for prv in private:
            if not prv:
                continue
            elif not prv.startswith('_'):
                prv = '_' + prv
            if prv not in self._private:
                self._private.append(prv)

    def set_configuration(self, new):
        warnings.warn("ConfigurationType.set_configuration is deprecated "
                      "in favor of the more Pythonic ConfigurationType.update", DeprecationWarning)
        self.update(new)

    def update(self, new):
        """
        Will update any configurations given through new.
        This method sets attributes on itself named after the configurations.
        Therefore be careful with using _private, _namespace, _defaults and _global_prefix as configurations.
        They will override attributes that the ConfigurationType needs internally.

        :param new: (dictionary) to update attributes on self with
        :return: None
        """
        if not new:
            return
        assert isinstance(new, dict), "Configurations can only be set with a dictionary not a {}".format(type(new))
        for key, value in new.items():
            # FEATURE: guard here against improper override of internal attributes
            shielded_key = key if key.startswith('_') else '_' + key
            if shielded_key in self._private:
                setattr(self, shielded_key, value)
            else:
                setattr(self, key, value)

    def _get_configuration(self, config):
        """
        This function tries to find configurations on self other than configurations set as direct attributes.

        It will first try to append a _ to the configuration to see if the configuration is protected/private.
        Then it will append a $ to the configuration to see if it is configuration from user input
        Then it will prefix the configuration with self._namespace
        and see if it exists on the defaults object as an attribute.
        If the configuration still isn't found it will prefix with self._global_prefix
        and look again for that as an attribute on defaults object.
        Finally it will raise a ConfigurationNotFoundError if the configuration is not there.

        NB: if you haven't set self._namespace it will default to self._global_prefix

        :param config: (string) name of the configuration to search for
        :return: (mixed) the configuration variable
        """
        shielded_key = '_' + config
        variable_key = '$' + config
        namespace_attr = self._namespace + '_' + config
        global_attr = self._global_prefix + '_' + config

        if shielded_key in self.__dict__:
            return self.__dict__[shielded_key]
        elif variable_key in self.__dict__:
            return self.__dict__[variable_key]

        # Lazy load the default configuration from settings to allow apps to register their own defaults
        if self._defaults is None:
            self._defaults = DATAGROWTH_DEFAULT_CONFIGURATION

        if namespace_attr in self._defaults:
            return self._defaults[namespace_attr]
        elif global_attr in self._defaults:
            return self._defaults[global_attr]
        else:
            raise ConfigurationNotFoundError(
                "Tried to retrieve '{}' in config and namespace '{}', without results.".format(config, self._namespace)
            )

    def to_dict(self, protected=False, private=False):
        """
        Will return the current configuration in dict form.
        By default it will return all attributes except those that are considered protected or private.
        Any configuration whose name starts with an _ is considered protected.
        Configurations are considered private when they start with _
        and are listed as private during initialisation of the configuration property.

        :param protected: (boolean) flag to include protected configurations
        :param private: (boolean) flag to include private configurations
        :return: (dict) current configuration other than default
        """
        return dict(self.items(protected=protected, private=private))

    @classmethod
    def from_dict(cls, config, defaults=None):
        """
        Creates a configuration using a dictionary.
        The dictionary should hold the appropriate _private and _namespace values.
        The _private value specifies which configurations should not be passed on
        to configuration that use this configuration as a base.
        The _namespace value specifies which prefix should be used to search default configurations,
        when a key can not be found in the configuration.

        :param config: (dict) the configuration keys and values to create a configuration with
        :param defaults: (dict) the configuration keys and values that act as a fallback
            or None to load defaults from settings at runtime
        :return: a configuration instance
        """
        assert isinstance(config, dict), \
            "Config should be a dict which values are the configurations."
        assert "_namespace" in config, \
            "_namespace needs to be specified in the configuration."
        assert "_private" in config, \
            "_private needs to be specified in the configuration."
        assert isinstance(defaults, dict) or defaults is None, \
            "Defaults should be a dict which values are the configuration defaults."
        instance = cls(
            defaults=defaults,
            namespace=config["_namespace"],
            private=config["_private"]
        )
        instance.update(config)
        return instance

    def supplement(self, other):
        """
        This method updates the configuration with keys from other
        if the configuration key does not exist in the configuration already.
        This allows configurations to update with only new values.

        :param other: (dict) the configuration keys and values to possibly update the configuration with
        :return: None
        """
        supplement = {}
        for key, value in other.items():
            if key not in self:
                supplement[key] = value
        if supplement:
            self.update(supplement)

    def items(self, protected=False, private=False):
        """
        Iterates over all configurations in a (key, value,) manner.
        It allows to skip over protected and private configurations, which happens by default.

        :param protected: (boolean) flag to include protected configurations
        :param private: (boolean) flag to include private configurations
        :return:
        """
        for key, value in self.__dict__.items():
            if key == '_defaults':
                continue
            if key.startswith('_'):
                if (private and key in self._private) or (protected and key not in self._private):
                    yield key, value
            else:
                yield key, value

    @staticmethod
    def clean_key(key):
        """
        Strips characters from the input key that have a special meaning to the configuration type.
        Namely '$' and '_'.

        :param key: (string) the key to strip special characters from
        :return: (string) the original or stripped key
        """
        if key.startswith("$") or key.startswith("_"):
            return key[1:]
        return key

    def __getattr__(self, item):
        item = self.clean_key(item)
        return self._get_configuration(item)

    def get(self, item, *args, **kwargs):
        """
        Getter for configuration item.
        When the configuration key is not found it raises a ConfigurationNotFoundError unless default is specified.
        If this is the case it returns the default instead.

        :param item: (string) key to get a configuration value for
        :param default: (mixed) value to return if configuration does not exist
        :return: (mixed) the configuration value or the default value
        """
        item = self.clean_key(item)

        if "default" in kwargs or len(args):
            default = kwargs.get("default", args[0])
            return getattr(self, item, default)
        else:
            return getattr(self, item)

    def __contains__(self, item):
        item = self.clean_key(item)
        try:
            getattr(self, item)
        except ConfigurationNotFoundError:
            return False
        return True

    def __str__(self):
        return str(self.to_dict(protected=True))


class ConfigurationProperty(object):
    """
    Initialize this class to place a configuration property upon another class.
    The property will be of the ConfigurationType described below. Upon initialization you can specify defaults.
    The defaults get returned when configurations are not explicitly set.
    There are two types of defaults:

        - Any configuration with a prefixes of `global` will be a default for all configuration properties
        - Any configuration with a prefix equal to namespace will be a default for configuration properties that share the namespace

    If you for example add `my_scoped_config`. Then configuration properties with the namespace set to `my` will
    return the `my_scoped_config` value if `scoped_config` is not set.

    :param storage_attribute: (string) name of the attribute used to store configurations on the owner class
    :param defaults: (dict) should hold default configurations as items
        or None to load defaults from settings at runtime
    :param namespace: (string) prefix to search default configurations with
    :param private: (list) keys that are considered as private for this property
    :return: ConfigurationType
    """

    def __init__(self, storage_attribute, defaults, namespace, private):
        """
        Runs some checks to create a ConfigurationType successfully upon first access of the property.

        :param storage_attribute: (string) name of the attribute used to store configurations on the owner class
        :param defaults: (dict) should hold default configurations as items
            or None to load defaults from settings at runtime
        :param namespace: (string) prefix to search default configurations with
        :param private: (list) keys that are considered as private for this property
        :return: ConfigurationType
        """
        assert storage_attribute, \
            "Specify a storage_attribute to store the configuration in."
        self._storage_attribute = storage_attribute
        self._defaults = defaults
        self._namespace = namespace
        self._private = private

    def __get__(self, obj, cls=None):
        if obj is None:  # happens with system checks
            return self
        elif not self._storage_attribute in obj.__dict__ or not obj.__dict__[self._storage_attribute]:
            obj.__dict__[self._storage_attribute] = ConfigurationType(
                defaults=self._defaults,
                namespace=self._namespace,
                private=self._private
            )
        return obj.__dict__[self._storage_attribute]

    def __set__(self, obj, new):
        if self._storage_attribute not in obj.__dict__:
            obj.__dict__[self._storage_attribute] = ConfigurationType(
                defaults=self._defaults,
                namespace=self._namespace,
                private=self._private
            )
        if isinstance(new, ConfigurationType):
            obj.__dict__[self._storage_attribute].update(
                new.to_dict(private=True, protected=True)
            )
        else:
            obj.__dict__[self._storage_attribute].update(new)


def create_config(namespace, configuration):
    """
    Use this function to quickly create a configuration.
    You need to specify under which namespace the configuration should search for defaults.
    The configuration names and their values need to be supplied as well as a simple dictionary.

    Apart from that the configuration needs no setup and the most common use cases will be supported.

    :param namespace: (str) the namespace under which missing configurations should be searched when defaulting
    :param values: (dict) the configuration keys and values that should be set on the configuration instance
    :return: ConfigurationType
    """
    config = ConfigurationType(
        namespace=namespace,
        private=("_private", "_namespace", "_defaults",)
    )
    config.update(configuration)
    return config


def register_defaults(namespace, configuration):
    """
    This function updates a global configuration defaults object with your own defaults.
    That way an application can set defaults at runtime during a configure stage like the Django apps ready hook.

    You need to specify under which namespace the configuration should become available.
    This should be the same as the namespace you create configurations with.
    You can provide the default configuration for that namespace as a simple dictionary.

    :param namespace: (str) the namespace under which the defaults will be registered.
    :param configuration: (dict) the configuration keys and values that should be set as defaults
    :return: None
    """
    defaults = {
        "{}_{}".format(namespace, key): value
        for key, value in configuration.items()
    }
    DATAGROWTH_DEFAULT_CONFIGURATION.update(defaults)
