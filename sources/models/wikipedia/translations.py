from __future__ import unicode_literals, absolute_import, print_function, division

from core.utils.helpers import override_dict
from core.exceptions import DSHttpError40X
from sources.models.wikipedia.query import WikipediaQuery


class WikipediaTranslate(WikipediaQuery):

    URI_TEMPLATE = 'http://{}.wiktionary.org/w/api.php?{}={}&iwprefix={}'  # updated at runtime

    PARAMETERS = override_dict(WikipediaQuery.PARAMETERS, {
        'prop': 'info|pageprops|iwlinks',
        'iwprop': 'url',
    })

    # HIF_objective = {
    #     "url": None,
    #     "*": None,
    #     "prefix": None
    # }
    # HIF_translations = {
    #     "*": "translation",
    #     "prefix": "language"
    # }

    def send(self, method, *args, **kwargs):
        args += (self.config.translate_to,)
        return super(WikipediaTranslate, self).send(method, *args, **kwargs)

    def _handle_errors(self):
        super(WikipediaTranslate, self)._handle_errors()
        if not "iwlinks" in self.body:
            self.status = 404
            raise DSHttpError40X("No translations found in {} for {}".format(self.meta), resource=self)

    @property
    def meta(self):
        try:
            return self.request["args"][0], self.request["args"][1]
        except (KeyError, IndexError, TypeError):
            return None, None