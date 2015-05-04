from legacy.models.settings import Domain


class Config(object):

    _private_defaults = ["_private", "_domain", "_namespace"]

    def __init__(self, namespace, private):
        """
        On init the domain gets set, which holds default values for configuration.
        The default config can be found on Domain object as an attribute like <namespace>_<config>
        Namespace is also set on init and can be given to this constructor.
        Last but not least a list with private keys can be given to this constructor.
        It will add those to the default ones set on this class.
        Private keys begin with an underscore. They won't get passed on by the dict function by default.
        """
        super(Config, self).__init__()
        self._domain = Domain()
        self._namespace = namespace
        self._private = self._private_defaults + [prv for prv in private if prv not in self._private_defaults]

    def __call__(self, new):
        """
        Calling an instance will set attributes which then can be accessed from there on.
        It won't delete any attributes, it only adds or updates them.
        """
        for key, value in new.iteritems():
            setattr(self, key, value)

    def __getattr__(self, item):
        """
        Here is where the magic happens :)
        This function gets called when attribute is not found on the object itself.
        We check whether the <namespace>_<item> attribute exists on Domain object.
        If it does we return that, if it doesn't we raise AttributeError.
        """
        if hasattr(self._domain, self._namespace + '_' + item):
            return getattr(self._domain, self._namespace + '_' + item)
        elif hasattr(self._domain, 'HIF_' + item):  # TODO: test getting default from HIF
            return getattr(self._domain, 'HIF_' + item)
        else:
            raise AttributeError("Tried to retrieve '{}' in config and namespace '{}', without results.".
                format(item, self._namespace))

    def __str__(self):
        return str(self.dict())

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
            if isinstance(value,str):
                value = unicode(value)
            if key == '_domain':
                continue
            if key.startswith('_'):
                if (private and key in self._private) or (protected and key not in self._private):
                    dictionary[key] = value
            else:
                dictionary[key] = value
        return dictionary