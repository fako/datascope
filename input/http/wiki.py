from HIF.input.http.links import JsonQueryLink


class WikiTranslate(JsonQueryLink):

    _link = 'http://{}.wiktionary.org/w/api.php' # updated at runtime
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

    def __init__(self, source=None, destination=None, *args, **kwargs):
        super(WikiTranslate, self).__init__(*args, **kwargs)
        self._link = self._link.format(source)
        self._parameters['iwprefix'] = destination

    class Meta:
        proxy = True
