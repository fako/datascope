from HIF.input.http.core import JsonQueryLink


class WikiTranslate(JsonQueryLink):

    HIF_link = 'http://{}.wiktionary.org/w/api.php' # updated at runtime
    HIF_parameters = {
        'format':'json',
        'action':'query',
        'prop':'iwlinks',
        'iwurl':1,
        'iwprefix': None,  # set at runtime
    }
    HIF_objective = {
        "url": None,
        "*": None,
    }
    HIF_translations = {
        "*": "translation"
    }
    HIF_query_parameter = 'titles'

    HIF_namespace = "wiki"

    def prepare_link(self):
        """
        .........
        """
        self.HIF_link = self.HIF_link.format(self.config.source_language)
        return super(WikiTranslate, self).prepare_link()

    def prepare_params(self):
        """
        .........
        """
        self.HIF_parameters['iwprefix'] = self.config.translate_to
        return super(WikiTranslate, self).prepare_params()

    class Meta:
        app_label = "HIF"
        proxy = True
