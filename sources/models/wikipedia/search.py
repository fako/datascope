from __future__ import unicode_literals, absolute_import, print_function, division

from copy import copy

from core.utils.helpers import override_dict
from core.exceptions import DSHttpWarning300

from sources.models.wikipedia.query import WikipediaQuery
from sources.models.wikipedia.mixins import WikipediaImagesMixin


class WikipediaSearch(WikipediaQuery, WikipediaImagesMixin):

    URI_TEMPLATE = 'http://{}.wikipedia.org/w/api.php?{}={}'
    PARAMETERS = override_dict(WikipediaQuery.PARAMETERS, {
        "prop": "info|pageprops|extracts",
        "exintro": 1,
    })
    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [{"type": "string"}],
            "minItems": 3,
            "maxItems": 3
        },
        "kwargs": None
    }

    def parameters(self):
        parameters = copy(self.PARAMETERS)
        parameters["exintro"] = int(not self.config.wiki_full_extracts)
        return parameters

    def _handle_errors(self):
        """
        Handle ambiguity errors
        """
        response = super(WikipediaSearch, self)._handle_errors()
        if isinstance(response, dict):
            for page_id, page in response.iteritems():
                try:
                    if "disambiguation" in page['pageprops']:
                        self.status = 300
                        raise DSHttpWarning300("The search is ambiguous.", resource=self)
                except KeyError:
                    pass
