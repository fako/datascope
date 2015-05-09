import json

from django.db.models import fields
from django.utils import six


class ConfigurationNotFoundError(Exception):
    pass


class ConfigurationType(object):

    _private_defaults = ["_private", "_defaults", "_namespace"]
    _global_prefix = "global"

    def __init__(self, defaults, namespace, private):
        # TODO: update comments
        """
        On init the domain gets set, which holds default values for configuration.
        The default config can be found on Domain object as an attribute like <namespace>_<config>
        Namespace is also set on init and can be given to this constructor.
        Last but not least a list with private keys can be given to this constructor.
        It will add those to the default ones set on this class.
        Private keys begin with an underscore. They won't get passed on by the dict function by default.
        """
        assert isinstance(defaults, object), "Defaults should be an object with attributes set as the configuration defaults."
        assert isinstance(namespace, six.string_types), "Namespaces should be a string that acts as a prefix for finding configurations."
        assert isinstance(private, (list, tuple,)), "Private should be a list or tuple of private configurations."

        super(ConfigurationType, self).__init__()
        self._defaults = defaults
        self._namespace = namespace or self._global_prefix
        self._private = self._private_defaults + [prv for prv in private if prv not in self._private_defaults]


    def __getattr__(self, item):
        print "inside getattr"
        return self.get_configuration(item)

    def get_configuration(self, item):
        """
        Here is where the magic happens :)
        This function gets called when attribute is not found on the object itself.
        We check whether the <namespace>_<item> attribute exists on default object.
        If it does we return that, if it doesn't we raise AttributeError.
        """
        namespace_key = self._namespace + '_' + item
        shielded_key = self._namespace + '__' + item
        global_key = self._global_prefix + '_' + item

        # Check for default configuration
        if hasattr(self._defaults, namespace_key):
            return getattr(self._defaults, self._namespace + '_' + item)
        elif hasattr(self._defaults, shielded_key):
            return getattr(self._defaults, self._namespace + '_' + item)
        # Check for global default configuration
        elif hasattr(self._defaults, global_key):  # TODO: test getting configuration with global prefix
            return getattr(self._defaults, self._global_prefix + item)
        # Not found
        else:
            raise ConfigurationNotFoundError(
                "Tried to retrieve '{}' in config and namespace '{}', without results.".format(item, self._namespace)
            )

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
        for key, value in self.iteritems():
            if isinstance(value, str):
                value = unicode(value)
            if key == '_domain':
                continue
            if key.startswith('_'):
                if (private and key in self._private) or (protected and key not in self._private):
                    dictionary[key] = value
            else:
                dictionary[key] = value
        return dictionary


class ConfigurationProperty(object):

    def __init__(self, storage_attribute, namespace, private, defaults):
        self._storage_attribute = storage_attribute
        self._namespace = namespace
        self._private = private
        self._defaults = defaults

    def __get__(self, obj, type=None):
        print "inside get"
        if obj is None:
            # TODO: warning, not bound
            return self
        elif not obj.__dict__[self._storage_attribute]:
            obj.__dict__[self._storage_attribute] = ConfigurationType(
                namespace=self._namespace,
                private=self._private,
                defaults=self._defaults
            )

        return obj.__dict__[self._storage_attribute]

    def __set__(self, obj, new):
        """
        Setting this type will update the dictionary on the owner
        It won't delete any keys, it only adds or updates them.
        """
        print "inside set"
        assert isinstance(new, dict), "Configurations can only be set with a dictionary"
        if self._storage_attribute not in obj.__dict__:
            obj.__dict__[self._storage_attribute] = ConfigurationType(
                namespace=self._namespace,
                private=self._private,
                defaults=self._defaults
            )

        for key, value in new.iteritems():
            setattr(obj.__dict__[self._storage_attribute], key, value)
        #obj.__dict__[self.field.name] = self.field.to_python(value)


class ConfigurationField(fields.TextField):

    def __init__(self, default_configuration=None, namespace="", private=[], *args, **kwargs):
        super(ConfigurationField, self).__init__(*args, **kwargs)
        self._default_configuration = default_configuration
        self._namespace = namespace
        self._private = private

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(ConfigurationField, self).contribute_to_class(cls, name)
        config_property = ConfigurationProperty(
            "_" + name,
            self._namespace,
            self._private,
            self._default_configuration
        )
        setattr(cls, self.name, config_property)

    def to_python(self, value):
        print "TO PYTHON", json.loads(value)
        value = super(ConfigurationField, self).to_python(value)
        return value

    def get_prep_value(self, value):
        print "HERE WE GO!", json.dumps(value)
        value = super(ConfigurationField, self).get_prep_value(value)
        return value
