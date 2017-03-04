from core.utils.helpers import override_dict
from sources.models.wikipedia.query import WikipediaGenerator


class WikipediaTransclusions(WikipediaGenerator):

    PARAMETERS = override_dict(WikipediaGenerator.PARAMETERS, {
        "generator": "transcludedin",
        "gtishow": "!redirect",
        "gtilimit": 500
    })