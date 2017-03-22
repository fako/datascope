from core.processors.rank import RankProcessor


class WikipediaRankProcessor(RankProcessor):

    def get_hook_arguments(self, individual):
        individual_argument = super(WikipediaRankProcessor, self).get_hook_arguments(individual)[0]
        wikidata_argument = individual_argument.get("wikidata", {})
        if wikidata_argument is None or isinstance(wikidata_argument, str):
            wikidata_argument = {}
        return [individual_argument, wikidata_argument]

    @staticmethod
    def revision_count(page, wikidata):
        return len(page.get("revisions", []))

    @staticmethod
    def category_count(page, wikidata):
        return len(page.get("categories", []))

    @staticmethod
    def number_of_deaths(page, wikidata):
        number_of_deaths_property = "P1120"
        return next(
            (claim["value"] for claim in wikidata.get("claims", [])
            if claim["property"] == number_of_deaths_property)
        , 0)

    @staticmethod
    def women(page, wikidata):
        sex_property = "P21"
        women_item = "Q6581072"
        return any(
            (claim for claim in wikidata.get("claims", [])
            if claim["property"] == sex_property and claim["value"] == women_item)
        )
