from __future__ import unicode_literals, absolute_import, print_function, division
import six

from core.processors.rank import RankProcessor


class WikipediaRankProcessor(RankProcessor):

    @staticmethod
    def revision_count(page):
        return len(page.get("revisions", []))

    @staticmethod
    def category_count(page):
        return len(page.get("categories", []))

    @staticmethod
    def number_of_deaths(page):
        wikidata = page.get("wikidata")
        if not wikidata or not isinstance(wikidata, six.string_types):
            return
        number_of_deaths_property = "P1120"
        for claim in wikidata.get("claims", []):
            if claim["property"] == number_of_deaths_property:
                return claim["value"]
        return

    @staticmethod
    def women(page):
        wikidata = page.get("wikidata")
        if not wikidata or isinstance(wikidata, six.string_types):
            return
        sex_property = "P21"
        women_item = "Q6581072"
        for claim in wikidata.get("claims", []):
            if claim["property"] == sex_property and claim["value"] == women_item:
                return True
        return
