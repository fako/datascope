import json
import logging

from django.db.models import fields
from django.utils import six


log = logging.getLogger(__name__)


class ConfigurationNotFoundError(Exception):
    pass


class ConfigurationType(object):

    _private_defaults = ["_private", "_defaults", "_namespace"]
    _global_prefix = "global"

    def __init__(self, namespace, private, defaults):
        # TODO: update comments
        """
        On init the domain gets set, which holds default values for configuration.
        The default config can be found on Domain object as an attribute like <namespace>_<config>
        Namespace is also set on init and can be given to this constructor.
        Last but not least a list with private keys can be given to this constructor.
        It will add those to the default ones set on this class.
        Private keys begin with an underscore. They won't get passed on by the dict function by default.
        """
        assert isinstance(defaults, object), \
            "Defaults should be an object with attributes set as the configuration defaults."
        assert isinstance(namespace, six.string_types), \
            "Namespaces should be a string that acts as a prefix for finding configurations."
        assert isinstance(private, (list, tuple,)), \
            "Private should be a list or tuple of private configurations."

        super(ConfigurationType, self).__init__()
        self._defaults = defaults
        self._namespace = namespace or self._global_prefix
        self._private = self._private_defaults + [prv for prv in private if prv not in self._private_defaults]

    def __getattr__(self, item):
        return self.get_configuration(item)

    def get_configuration(self, item):
        """
        Here is where the magic happens :)
        This function gets called when attribute is not found on the object itself.
        We check whether the <namespace>_<item> attribute exists on default object.
        If it does we return that, if it doesn't we raise AttributeError.
        """
        shielded_attr = '_' + item
        namespace_attr = self._namespace + '_' + item
        shielded_namespace_attr = self._namespace + '__' + item
        global_attr = self._global_prefix + '_' + item

        if shielded_attr in self.__dict__:
            return self.__dict__[shielded_attr]
        if hasattr(self._defaults, namespace_attr):
            return getattr(self._defaults, namespace_attr)
        if hasattr(self._defaults, shielded_namespace_attr):
            return getattr(self._defaults, shielded_namespace_attr)
        elif hasattr(self._defaults, global_attr):  # TODO: test getting configuration with global prefix
            return getattr(self._defaults, global_attr)
        else:
            raise ConfigurationNotFoundError(
                "Tried to retrieve '{}' in config and namespace '{}', without results.".format(item, self._namespace)
            )

    def set_configuration(self, new):
        """
        Setting this type will update the dictionary on the owner
        It won't delete any keys, it only adds or updates them.
        """
        assert isinstance(new, dict), "Configurations can only be set with a dictionary not a {}".format(type(new))
        for key, value in new.iteritems():
            setattr(self, key, value)

    def __str__(self):
        return str(self.dict())  # TODO: why? unicode? only self?

    def dict(self, protected=False, private=False):
        """
        Will return the current configuration in dict form.
        By default it will return all attributes except those that start with an underscore.
        If protected=True is given it will return attributes starting with underscore that are not marked as private.
        If private=True is given it will return attributes starting with underscore that are marked as private.
        It never returns domain attribute, because that attribute is the same for all config instances.
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


class ConfigurationProperty(object):
    """
    This class only creates a property that manages a ConfigurationType instance on the owner class.
    """
    def __init__(self, storage_attribute, namespace, private, defaults):
        self._storage_attribute = storage_attribute
        self._namespace = namespace
        self._private = private
        self._defaults = defaults

    def __get__(self, obj, type=None):
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
        if isinstance(new, six.string_types):
            try:
                new = json.loads(new)
            except ValueError:
                log.warning("Could not load a dictionary for ConfigurationType from set value.")
        obj.__dict__[self._storage_attribute].set_configuration(new)


class ConfigurationField(fields.TextField):

    def __init__(self, namespace="", private=[], default=None, *args, **kwargs):
        """
        This field creates a property of ConfigurationType on the model.



        :param namespace:
        :param private:
        :param default_configuration:
        :param args:
        :param kwargs:
        :return:
        """
        assert isinstance(default, object), \
            "Default configuration should be an object with attributes set as the configuration defaults."
        assert isinstance(namespace, six.string_types), \
            "Namespaces should be a string that acts as a prefix for finding configurations."
        assert isinstance(private, (list, tuple,)), \
            "Private should be a list or tuple of private configurations."

        super(ConfigurationField, self).__init__(*args, **kwargs)
        self._default = default
        self._namespace = namespace
        self._private = private

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(ConfigurationField, self).contribute_to_class(cls, name)
        configuration_property = ConfigurationProperty(
            "_" + name,
            self._namespace,
            self._private,
            self._default
        )
        setattr(cls, self.name, configuration_property)

    def to_python(self, value):
        dictionary = json.loads(value)
        return super(ConfigurationField, self).to_python(dictionary)

    def get_prep_value(self, value):
        json_dict = json.dumps(value.dict(protected=True, private=True))
        return super(ConfigurationField, self).get_prep_value(json_dict)
