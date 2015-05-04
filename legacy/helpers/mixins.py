from legacy.helpers.data import json_extractor


class DataMixin(object):
    """
    This mixin adds a results property to the mother class
    Using the _objective and _translations HIF interface vars the mixin will
    """

    # HIF interface vars
    HIF_objective = {}
    HIF_translations = {}

    def __init__(self):
        self._data = []

    def __iter__(self):
        return iter(self.data)

    @property
    def data_source(self):
        return []

    @property
    def data(self):
        """
        Extracts results, translates them and filters them before returning it
        """
        self.extract(self.data_source).translate()
        return filter(self.cleaner, self._data)

    def extract(self, source):
        """
        Should extract results from source using _objective and puts them in self.rsl
        The way this is done depends on the type of data in self.source
        This base class is not concerned with types of data and thus does nothing
        """
        self._data = source
        return self

    def translate(self):
        """
        Changes keys in all dicts under self.rsl to reflect keys in _translations
        """
        if self.HIF_translations:
            for raw in self._data:
                for key,replacement in self.HIF_translations.iteritems():
                    if key in raw:  # if a key that needs translation is found
                        raw[replacement] = raw[key] # make a new pair in result with the translated key as key
                        del(raw[key])  # delete the old key/value pair
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
        Extracts results from source using _objective and puts it in self.data
        It uses legacy.helpers.json_extractor to get the job done
        """
        self._data = json_extractor(source, self.HIF_objective)
        return self
