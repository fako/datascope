from core.utils.helpers import override_dict

from sources.models.wikipedia.query import WikipediaGenerator, WikipediaQuery


class WikipediaCategories(WikipediaQuery):

    PARAMETERS = override_dict(WikipediaQuery.PARAMETERS, {
        "cllimit": 500,
        "clshow": "",  # gets set at runtime through "wiki_show_categories" config with "!hidden" by default
        "prop": "categories"  # generator style: info|pageprops|categoryinfo
    })

    def variables(self, *args):
        show = args[3] if len(args) > 3 else self.PARAMETERS["clshow"]
        variables = super(WikipediaCategories, self).variables(*args[:3])
        variables["show"] = show
        return variables

    def parameters(self, **kwargs):
        params = dict(self.PARAMETERS)
        params["clshow"] = self.config.wiki_show_categories
        return params

    class Meta:
        verbose_name = "Wikipedia category"
        verbose_name_plural = "Wikipedia categories"


class WikipediaCategoryMembers(WikipediaGenerator):

    PARAMETERS = override_dict(WikipediaGenerator.PARAMETERS, {
        "generator": "categorymembers",
        "gcmlimit": 100,
        "gcmnamespace": 0,
        "prop": "info|pageprops|categories",
        "clshow": "!hidden",
        "cllimit": 500,
    })

    WIKI_QUERY_PARAM = "gcmtitle"

    class Meta:
        verbose_name = "Wikipedia category members"
        verbose_name_plural = "Wikipedia category members"
