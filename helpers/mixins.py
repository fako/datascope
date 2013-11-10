from django.db import models

from HIF.helpers.extractors import json_extractor
from HIF.models.settings import Domain


class Config(object):

    def __init__(self, namespace):
        super(Config, self).__init__()
        self.domain = Domain()
        self.namespace = namespace

    def __getattr__(self, item):
        if hasattr(self.domain, self.namespace + '_' + item):
            return getattr(self.domain, self.namespace + '_' + item)
        else:
            raise AttributeError("Tried to retrieve '{}' in config and namespace '{}', without results.".format(item, self.namespace))

    def __call__(self, new):
        for key,value in new.iteritems():
            setattr(self, key, value)

    def __str__(self):
        return str(self.dict())

    def dict(self):
        dictionary = dict(self.__dict__)
        if "domain" in dictionary: del(dictionary["domain"])
        if "namespace" in dictionary: del(dictionary["namespace"])
        return dictionary


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
        self.config = Config(self._config_namespace)
        for key,value in config.iteritems():
            setattr(self.config,key,value)


class DataMixin(object):
    """
    This mixin adds a results property to the mother class
    Using the _objective and _translations HIF interface vars the mixin will
    """

    # class attributes
    rsl = []

    # HIF interface vars
    _objective = {}
    _translations = {}

    def __iter__(self):
        return iter(self.results)

    @property
    def source(self):
        return []

    @property
    def results(self):
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
        self.rsl = source
        return self

    def translate(self):
        """
        Changes keys in all dicts under self.rsl to reflect keys in _translations
        """
        if self._translations:
            for r in self.rsl:
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
        self.rsl = json_extractor(source, self._objective)
        return self
