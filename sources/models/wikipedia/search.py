from __future__ import unicode_literals, absolute_import, print_function, division

import re
from copy import copy

from core.utils.helpers import override_dict
from core.exceptions import DSHttpWarning300

from sources.models.wikipedia.query import WikipediaQuery


class WikipediaSearch(WikipediaQuery):

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

    CONFIG_NAMESPACE = "wikipedia"
    WIKI_RESULTS_KEY = "pages"

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

    @property
    def content(self):
        if not self._json_body:
            # We're gonna make some hackish changes to the raw response
            original_body = copy(self.body)
            # Replace image references with absolute URL's
            images = re.findall('"page_image": ?"([^"]+)"', self.body)
            for image in images:
                self.body = self.body.replace(image, self.get_wiki_image(image), 1)
            # Converting and make sure this method acts functional
            content_type, data = super(WikipediaSearch, self).content
            self.body = original_body
            self._json_body = data
        return "application/json", self._json_body

    def __init__(self, *args, **kwargs):
        super(WikipediaQuery, self).__init__(*args, **kwargs)
        self._json_body = None
