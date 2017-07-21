from core.utils.helpers import override_dict

from sources.models.wikipedia.query import WikipediaGenerator, WikipediaQuery


class WikipediaCategories(WikipediaQuery):

    PARAMETERS = override_dict(WikipediaQuery.PARAMETERS, {
        "cllimit": 500,
        "clshow": "!hidden",  # might get altered secondary get argument
        "prop": "categories"
    })

    def variables(self, *args):
        show = args[3] if len(args) > 3 else self.PARAMETERS["clshow"]
        variables = super(WikipediaCategories, self).variables(*args[:3])
        variables["show"] = show
        return variables

    def parameters(self, **kwargs):
        params = dict(self.PARAMETERS)
        params["clshow"] = kwargs["show"]
        return params


class WikipediaCategoryMembers(WikipediaGenerator):

    PARAMETERS = override_dict(WikipediaGenerator.PARAMETERS, {
        "generator": "categorymembers",
        "gcmlimit": 500,
        "gcmnamespace": 0,
        "prop": "info"
    })

    WIKI_QUERY_PARAM = "gcmtitle"
