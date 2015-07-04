from __future__ import unicode_literals, absolute_import, print_function, division

from core.utils.helpers import override_dict
from core.exceptions import DSHttpError40X, DSInvalidResource
from sources.models.wikipedia.query import WikipediaQuery


class WikipediaTranslate(WikipediaQuery):

    URI_TEMPLATE = 'http://{}.wiktionary.org/w/api.php?{}={}&iwprefix={}'  # updated at runtime

    PARAMETERS = override_dict(WikipediaQuery.PARAMETERS, {
        'prop': 'info|pageprops|iwlinks',
        'iwprop': 'url',
    })

    def _handle_errors(self):
        super(WikipediaTranslate, self)._handle_errors()
        if not "iwlinks" in self.body:
            self.status = 404
            raise DSHttpError40X("No translations found in {} for {}".format(self.meta), resource=self)

    @property
    def content(self):
        content_type, data = super(WikipediaQuery, self).content
        try:
            page = data["query"]["pages"].values()[0]
        except (KeyError, IndexError):
            raise DSInvalidResource(
                "Translate resource did not contain 'query', 'pages' or a first page",
                resource=self
            )
        data["page"] = page
        return content_type, data

    @property
    def meta(self):
        try:
            return self.request["args"][0], self.request["args"][1]
        except (KeyError, IndexError, TypeError):
            return None, None