from core.utils.helpers import override_dict
from sources.models.wikipedia.query import WikipediaGenerator


class WikipediaTransclusions(WikipediaGenerator):

    PARAMETERS = override_dict(WikipediaGenerator.PARAMETERS, {
        "generator": "transcludedin",
        "gtishow": "!redirect",
        "gtilimit": 500
    })

    class Meta:
        verbose_name = "Wikipedia transclusions"
        verbose_name_plural = "Wikipedia transclusions"
