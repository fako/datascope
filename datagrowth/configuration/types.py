from copy import copy


class ConfigurationNotFoundError(AttributeError):
    pass


class ConfigurationType(object):
    """
    Instances of this type are configurations that can be serialized to JSON dicts for storage and transfer.
    They can also pass on their configuration to other instances in a parent/child like relationship.
    Upon initialization (which typically happens when application loads) defaults can be specified,
    which then may get overridden at runtime (typically during requests).
    """
    # FEATURE: protect against unexpected user input configurations

    _private_defaults = ["_private", "_defaults", "_namespace"]
    _global_prefix = "global"

    def __init__(self, defaults, namespace="", private=tuple()):
        """
        Initiates the ConfigurationType by checking arguments and setting logically private attributes

        :param defaults: (dict) that should hold default configurations as items
        :param namespace: (string) prefix to search default configurations with
        :param private: (list) keys that are considered as private
        :return: None
        """
        assert isinstance(defaults, dict), \
            "Defaults should be a dict which values are the configuration defaults."
        assert isinstance(namespace, str), \
            "Namespaces should be a string that acts as a prefix for finding configurations."
        assert isinstance(private, (list, tuple,)), \
            "Private should be a list or tuple of private configurations."

        super(ConfigurationType, self).__init__()
        self._defaults = defaults
        self._namespace = namespace or self._global_prefix
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

        By default it will return all attributes except those that start with an underscore.
        You can include protected and private configurations through arguments

        NB: It never returns the defaults attribute, because that attribute is the same for all instances.

        :param protected: (boolean) flag to include protected configurations
        :param private: (boolean) flag to include private configurations
        :return: (dict) current configuration other than default
        """
        return dict(self.items(protected=protected, private=private))

    @classmethod
    def from_dict(cls, config, defaults):
        assert isinstance(config, dict), \
            "Config should be a dict which values are the configurations."
        assert "_namespace" in config, \
            "_namespace needs to be specified in the configuration."
        assert "_private" in config, \
            "_private needs to be specified in the configuration."
        assert isinstance(defaults, dict), \
            "Defaults should be a dict which values are the configuration defaults."
        instance = cls(
            defaults=defaults,
            namespace=config["_namespace"],
            private=config["_private"]
        )
        instance.set_configuration(config)
        return instance

    def supplement(self, other):
        supplement = {}
        for key, value in other.items():
            if key not in self:
                supplement[key] = value
        if supplement:
            self.set_configuration(supplement)

    def items(self, protected=False, private=False):
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
        if key.startswith("$") or key.startswith("_"):
            return key[1:]
        return key

    def __getattr__(self, item):
        item = self.clean_key(item)
        return self._get_configuration(item)

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
    This class creates a property that manages a ConfigurationType instance on the owner class.
    """

    def __init__(self, storage_attribute, defaults, namespace, private):
        """
        Runs some checks to create a ConfigurationType successfully upon first access of the property.

        :param storage_attribute: (string) name of the attribute used to store configuration on owner of this property
        :param defaults: (dict) that should hold default configurations as items
        :param namespace: (string) prefix to search default configurations with
        :param private: (list) keys that are considered as private
        :return: None
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
