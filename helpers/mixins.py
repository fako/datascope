import json

from django.db import models

from HIF.helpers.extractors import json_extractor
from HIF.models.settings import Domain


class Config(object):

    _private = ["_private", "_domain", "_namespace"]

    def __init__(self, namespace, private):
        super(Config, self).__init__()
        self._domain = Domain()
        self._namespace = namespace
        self._private += private

    def __getattr__(self, item):
        if hasattr(self._domain, self._namespace + '_' + item):
            return getattr(self._domain, self._namespace + '_' + item)
        else:
            raise AttributeError("Tried to retrieve '{}' in config and namespace '{}', without results.".format(item, self._namespace))

    def __call__(self, new):
        for key,value in new.iteritems():
            setattr(self, key, value)

    def __str__(self):
        return str(self.dict())

    def dict(self, protected=False, private=False):
        dictionary = dict()
        for key, value in self.__dict__.iteritems():
            if key.startswith('_'):
                if (private and key in self._private) or (protected and key not in self._private):
                    dictionary[key] = value
            else:
                dictionary[key] = value
        return dictionary

    def json(self):
        return json.dumps(self.dict())


class ConfigMixin(object):

    def __init__(self, *args, **kwargs):
        # Default
        config = {}
        # Parse args
        try:
            config = args[0]
            if not isinstance(config, dict):
                config = {}
            else:
                args = args[1:] # removes config from args
        except IndexError:
            pass
        # Parse kwargs
        try:
            if not config:
                config = kwargs["config"]
            del(kwargs["config"])
        except KeyError:
            pass
        # Super and set config as attributes
        super(ConfigMixin, self).__init__(*args, **kwargs)
        self.config = Config(self.HIF_namespace, self.HIF_private)
        for key,value in config.iteritems():
            setattr(self.config,key,value)


class DataMixin(object):
    """
    This mixin adds a results property to the mother class
    Using the _objective and _translations HIF interface vars the mixin will
    """

    # class attributes
    data = []

    # HIF interface vars
    _objective = {}
    _translations = {}

    def __iter__(self):
        return iter(self.results)

    @property
    def source(self):
        return []

    @property
    def results(self): # TODO: rename to data
        """
        Extracts results, translates them and filters them before returning it
        """
        self.extract(self.source).translate()
        return filter(self.cleaner, self.rsl)

    def extract(self, source):
        """
        Should extract results from source using _objective and puts them in self.rsl
        The way this is done depends on the type of data in self.source
        This base class is not concerned with types of data and thus does nothing
        """
        self.data = source
        return self

    def translate(self):
        """
        Changes keys in all dicts under self.rsl to reflect keys in _translations
        """
        if self._translations:
            for r in self.data:
                for k,v in self._translations.iteritems():
                    if k in r: # if a key that needs translation is found
                        r[v] = r[k] # make a new pair in result with the translated key as key
                        del(r[k]) # delete the old key/value pair
        return self

    def cleaner(self,result_instance):
        """
        Should inspect result_instance and return True if the results should be included and False if not
        """
        return True


class JsonDataMixin(DataMixin):
    """
    This class delivers functionality like DataMixin, but especially for JSON data
    """
    def extract(self, source):
        """
        Extracts results from source using _objective and puts it in self.rsl
        It uses HIF.helpers.json_extractor to get the job done
        """
        self.data = json_extractor(source, self._objective)
        return self
