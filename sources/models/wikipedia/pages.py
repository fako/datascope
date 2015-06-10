from core.utils.helpers import override_dict

from sources.models.wikipedia.query import WikipediaQuery
from sources.models.wikipedia.mixins import WikipediaImagesMixin


class WikipediaListPages(WikipediaQuery, WikipediaImagesMixin):

    PARAMETERS = override_dict(WikipediaQuery.PARAMETERS, {
        "prop": "info|pageprops|categories",
        "clshow": "!hidden",
        "cllimit": 500
    })
    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [{"type": "string"}],  # TODO: validate with pattern?
            "minItems": 3,
            "maxItems": 3
        },
        "kwargs": None
    }
    WIKI_QUERY_PARAM = "pageids"
