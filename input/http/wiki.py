from HIF.input.http.links import JsonQueryLink


class WikiTranslate(JsonQueryLink):

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
