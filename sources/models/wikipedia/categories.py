from core.utils.helpers import override_dict

from sources.models.wikipedia.query import WikipediaGenerator


class WikipediaCategories(WikipediaGenerator):

    PARAMETERS = override_dict(WikipediaGenerator.PARAMETERS, {
        "generator": "categories",
        "gcllimit": 500,
        "gclshow": "!hidden",
        "prop": "info"
    })


class WikipediaCategoryMembers(WikipediaGenerator):

    PARAMETERS = override_dict(WikipediaGenerator.PARAMETERS, {
        "generator": "categorymembers",
        "gcmlimit": 500,
        "gcmnamespace": 0,
        "prop": "info"
    })

    WIKI_QUERY_PARAM = "gcmtitle"
