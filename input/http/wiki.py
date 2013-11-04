from HIF.input.http.core import JsonQueryLink


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
    _config = ["query", "source_language", "translate_to"]
    _config_namespace = "wiki"

    def prepare_link(self, *args, **kwargs):
        self._link = self._link.format(self.config.source_language)
        self._parameters['iwprefix'] = self.config.translate_to
        super(WikiTranslate, self).prepare_link(*args, **kwargs)

    class Meta:
        proxy = True
