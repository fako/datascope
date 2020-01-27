from copy import copy

from datagrowth.utils import override_dict
from datagrowth.exceptions import DGHttpWarning300

from sources.models.wikipedia.query import WikipediaQuery
from sources.models.wikipedia.mixins import WikipediaImagesMixin


class WikipediaSearch(WikipediaQuery, WikipediaImagesMixin):

    URI_TEMPLATE = 'http://{}.wikipedia.org/w/api.php?{}={}'
    PARAMETERS = override_dict(WikipediaQuery.PARAMETERS, {
        "prop": "info|pageprops|extracts|categories",
        "exintro": 1,
        "clshow": "!hidden",
        "cllimit": 500
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

    def parameters(self, **kwargs):
        parameters = copy(self.PARAMETERS)
        parameters["exintro"] = int(not self.config.wiki_full_extracts)
        return parameters

    def handle_errors(self):
        """
        Handle ambiguity errors
        """
        response = super(WikipediaSearch, self).handle_errors()
        if isinstance(response, dict):
            for page_id, page in response.items():
                try:
                    if "disambiguation" in page['pageprops']:
                        self.status = 300
                        raise DGHttpWarning300("The search is ambiguous.", resource=self)
                except KeyError:
                    pass

    class Meta:
        verbose_name = "Wikipedia search"
        verbose_name_plural = "Wikipedia searches"
