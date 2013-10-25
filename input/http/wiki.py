from HIF.models import DataLinkMixin
from HIF.input.http.base import QueryLink
from HIF.processors.extractors import json_extractor

class WikiLink(QueryLink, DataLinkMixin):

    def extract_results(self):
        return json_extractor(self.response, self._objective)

    def continue_request(self):
        pass


class WikiTranslate(WikiLink, DataLinkMixin):

    _link_type = 'WikiTranslate'
    _link = 'http://%s.wiktionary.org/w/api.php' # updated at runtime
    _parameters = {
        'format':'json',
        'action':'query',
        'prop':'iwlinks',
        'iwurl':1,
        'iwprefix': None, # set at runtime
    }
    _objective = {
        "url": None,
        "*": None,
    }
    _translations = {
        "*": "translation"
    }
    _query_parameter = 'titles'

    def __init__(self, source, destination, *args, **kwargs):
        super(WikiTranslate, self).__init__(*args, **kwargs)
        self._link = self._link % source
        self._parameters['iwprefix'] = destination
