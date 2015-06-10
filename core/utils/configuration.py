from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves.urllib.parse import parse_qsl

import json
import logging
import argparse
from copy import copy

from django.db.models import fields
from django.utils import six


log = logging.getLogger("datascope")


class ConfigurationNotFoundError(Exception):
    pass


class ConfigurationType(object):
    """
    This is the type for a ConfigurationProperty.

    """

    _private_defaults = ["_private", "_defaults", "_namespace"]
    _global_prefix = "global"

    def __init__(self, defaults, namespace="", private=tuple()):
        """
        Initiates the ConfigurationType by checking arguments and setting privates

        :param defaults: (dict) that should hold default configurations as items
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

        NB: Be careful with using _private, _namespace, _defaults and _global_prefix as configurations.
            They will override attributes that the ConfigurationType needs internally.

        :param new: (dictionary) to update attributes on self with
        :return: None
        """
        assert isinstance(new, dict), "Configurations can only be set with a dictionary not a {}".format(type(new))
        for key, value in new.iteritems():
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

    def __getattr__(self, item):
        return self._get_configuration(item)

    def __str__(self):
        return str(self.to_dict(protected=True))

    def __unicode__(self):
        return  unicode(self.to_dict(protected=True))


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
        if obj is None:
            log.warning("ConfigurationType not bound to an owner.")
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
            obj.__dict__[self._storage_attribute].set_configuration(
                new.to_dict(private=True, protected=True)
            )
        else:
            obj.__dict__[self._storage_attribute].set_configuration(new)


class ConfigurationField(fields.TextField):
    """
    This field creates a property of ConfigurationType on the model.

    NB: default that gets stored in the database is always an empty dictionary.
    """

    def __init__(self, config_defaults=None, namespace="", private=tuple(), default=None, *args, **kwargs):
        """
        Stores its arguments for later use by contribute_to_class.
        Assertions are done by the ConfigurationType class, upon contribute_to_class.

        :param config_defaults: (dict) that should hold default configurations as items
        :param namespace: (string) prefix to search default configurations with
        :param private: (list) keys that are considered as private
        :param args: additional field arguments
        :param kwargs: additional field keyword arguments
        :return:
        """
        super(ConfigurationField, self).__init__(default={}, *args, **kwargs)
        self._defaults = config_defaults if config_defaults else {}
        self._namespace = namespace
        self._private = private

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(ConfigurationField, self).contribute_to_class(cls, name)
        configuration_property = ConfigurationProperty(
            storage_attribute="_" + name,
            defaults=getattr(cls, 'CONFIG_DEFAULTS', self._defaults),
            namespace=getattr(cls, 'CONFIG_NAMESPACE', self._namespace),
            private=getattr(cls, 'CONFIG_PRIVATE', self._private)
        )
        setattr(cls, self.name, configuration_property)

    def from_db_value(self, value, expression, connection, context):
        return json.loads(value)

    def to_python(self, value):
        dictionary = json.loads(value)
        return super(ConfigurationField, self).to_python(dictionary)

    def get_prep_value(self, value):
        if not isinstance(value, dict):
            value = json.dumps(value.to_dict(protected=True, private=True))
        return super(ConfigurationField, self).get_prep_value(value)


def load_config(defaults):

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

    def __call__(self, parser, namespace, values, option_string=None):
        values = dict(parse_qsl(values))
        setattr(namespace, self.dest, values)
