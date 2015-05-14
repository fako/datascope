import json
import logging
from copy import copy

from django.db.models import fields
from django.utils import six


log = logging.getLogger("datascope")


class ConfigurationNotFoundError(Exception):
    pass


class ConfigurationType(object):

    _private_defaults = ["_private", "_defaults", "_namespace"]
    _global_prefix = "global"

    def __init__(self, defaults, namespace="", private=tuple()):
        """
        Initiates the Configuration type by running some checks and setting properties based on arguments.

        :param defaults: (object) that should hold default configurations as attributes
        :param namespace: (string) prefix to search default configurations with
        :param private: (list) keys that are considered as private
        :return: None
        """
        assert isinstance(defaults, dict), \
            "Defaults should be a dict which values are the configuration defaults."
        assert isinstance(namespace, six.string_types), \
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
        """
        Will update any keys in new with corresponding attributes on self.

        :param new: (dictionary) to update attributes on self with
        :return: None
        """
        assert isinstance(new, dict), "Configurations can only be set with a dictionary not a {}".format(type(new))
        for key, value in new.iteritems():
            setattr(self, key, value)

    def _get_configuration(self, config):
        """
        This function tries to find configurations on self other than configurations set as direct attributes.

        It will first try to append a _ to the configuration to see if the configuration is protected/private.
        Then it will prefix the configuration with self._namespace and see if it exists on the defaults object as an attribute.
        If the configuration still isn't found it will prefix with self._global_prefix and look again for that as an attribute on defaults object.
        Finally it will raise a ConfigurationNotFoundError if the configuration is not there.

        NB: if you haven't set self._namespace it will default to self._global_prefix

        :param config: (string) name of the configuration to search for
        :return: (mixed) the configuration variable
        """
        shielded_key = '_' + config
        namespace_attr = self._namespace + '_' + config
        global_attr = self._global_prefix + '_' + config

        if shielded_key in self.__dict__:
            return self.__dict__[shielded_key]
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

        NB: It never returns domain attribute, because that attribute is the same for all config instances.

        :param protected: (boolean) flag to include protected configurations
        :param private: (boolean) flag to include private configurations
        :return: (dict) current configuration other than default
        """
        dictionary = dict()
        for key, value in self.__dict__.iteritems():
            if isinstance(value, str):
                value = unicode(value)
            if key == '_defaults':
                continue
            if key.startswith('_'):
                if (private and key in self._private) or (protected and key not in self._private):
                    dictionary[key] = value
            else:
                dictionary[key] = value
        return dictionary

    def __getattr__(self, item):
        return self._get_configuration(item)

    def __str__(self):
        return str(self.to_dict(protected=True))

    def __unicode__(self):
        return  unicode(self.to_dict(protected=True))


class ConfigurationProperty(object):
    """
    This class only creates a property that manages a ConfigurationType instance on the owner class.
    """
    def __init__(self, storage_attribute, defaults, namespace, private):
        self._storage_attribute = storage_attribute
        self._defaults = defaults
        self._namespace = namespace
        self._private = private

    def __get__(self, obj, cls=None):
        if obj is None:
            log.warning("ConfigurationType not bound to an owner.")
            return self
        elif not obj.__dict__[self._storage_attribute]:
            obj.__dict__[self._storage_attribute] = ConfigurationType(
                namespace=self._namespace,
                private=self._private,
                defaults=self._defaults
            )

        return obj.__dict__[self._storage_attribute]

    def __set__(self, obj, new):
        if self._storage_attribute not in obj.__dict__:
            obj.__dict__[self._storage_attribute] = ConfigurationType(
                namespace=self._namespace,
                private=self._private,
                defaults=self._defaults
            )
        obj.__dict__[self._storage_attribute].set_configuration(new)


class ConfigurationField(fields.TextField):

    def __init__(self, default=None, namespace="", private=tuple(), *args, **kwargs):
        """
        This field creates a property of ConfigurationType on the model.

        NB: default that gets stored in the database is always an empty dictionary.

        :param defaults: (object) that should hold default configurations as attributes
        :param namespace: (string) prefix to search default configurations with
        :param private: (list) keys that are considered as private
        :param args: additional field arguments
        :param kwargs: additional field keyword arguments
        :return:
        """
        assert isinstance(default, object), \
            "Default configuration should be an object with attributes set as the configuration defaults."
        assert isinstance(namespace, six.string_types), \
            "Namespaces should be a string that acts as a prefix for finding configurations."
        assert isinstance(private, (list, tuple,)), \
            "Private should be a list or tuple of private configurations."

        super(ConfigurationField, self).__init__(*args, default={}, **kwargs)
        self._default = default
        self._namespace = namespace
        self._private = private

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(ConfigurationField, self).contribute_to_class(cls, name)
        configuration_property = ConfigurationProperty(
            storage_attribute="_" + name,
            defaults=self._default,
            namespace=self._namespace,
            private=self._private
        )
        setattr(cls, self.name, configuration_property)

    def from_db_value(self, value, expression, connection, context):
        return json.loads(value)

    def to_python(self, value):
        dictionary = json.loads(value)
        return super(ConfigurationField, self).to_python(dictionary)

    def get_prep_value(self, value):
        json_dict = json.dumps(value.to_dict(protected=True, private=True))
        return super(ConfigurationField, self).get_prep_value(json_dict)
