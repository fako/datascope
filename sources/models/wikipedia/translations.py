from __future__ import unicode_literals, absolute_import, print_function, division

from core.utils.helpers import override_dict
from core.exceptions import DSHttpError40X, DSInvalidResource
from sources.models.wikipedia.query import WikipediaPage


class WikipediaTranslate(WikipediaPage):

    URI_TEMPLATE = 'http://{}.wiktionary.org/w/api.php?{}={}&iwprefix={}'  # updated at runtime

    PARAMETERS = override_dict(WikipediaPage.PARAMETERS, {
        'prop': 'info|pageprops|iwlinks',
        'iwprop': 'url',
    })

    def _handle_errors(self):
        super(WikipediaTranslate, self)._handle_errors()
        if not "iwlinks" in self.body:
            self.status = 404
            raise DSHttpError40X("No translations found for {} in {}".format(*self.meta), resource=self)

    @property
    def meta(self):
        try:
            return self.request["args"][2], self.request["args"][3]
        except (KeyError, IndexError, TypeError):
            return None, None
