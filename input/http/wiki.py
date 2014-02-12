from HIF.input.http.core import JsonQueryLink


class WikiTranslate(JsonQueryLink):

    HIF_link = 'http://{}.wiktionary.org/w/api.php' # updated at runtime
    HIF_parameters = {
        'format': 'json',
        'action': 'query',
        'prop': 'iwlinks',
        'iwurl': 1,
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
        Prepare link does some pre formatting by including the source_language as a sub domain.
        """
        self.HIF_link = self.HIF_link.format(self.config.source_language)
        return super(WikiTranslate, self).prepare_link()

    def prepare_params(self):
        """
        Prepare params sets the inter wiki prefix as a parameter depending on the language to translate to.
        """
        self.HIF_parameters['iwprefix'] = self.config.translate_to
        return super(WikiTranslate, self).prepare_params()

    class Meta:
        app_label = "HIF"
        proxy = True
