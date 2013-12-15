from HIF.models.settings import Domain


class Config(object):  # TODO: tests

    _private = ["_private", "_domain", "_namespace"]

    def __init__(self, namespace, private):
        """

        """
        super(Config, self).__init__()
        self._domain = Domain()
        self._namespace = namespace
        self._private += [prv for prv in private if prv not in self._private]

    def __call__(self, new):
        """

        """
        for key, value in new.iteritems():
            setattr(self, key, value)

    def __getattr__(self, item):
        if hasattr(self._domain, self._namespace + '_' + item):
            return getattr(self._domain, self._namespace + '_' + item)
        else:
            raise AttributeError("Tried to retrieve '{}' in config and namespace '{}', without results.".format(item, self._namespace))

    def __str__(self):
        return str(self.dict())

    def dict(self, protected=False, private=False):
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