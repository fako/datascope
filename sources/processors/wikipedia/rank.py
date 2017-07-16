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
    def editor_count(page, wikidata):
        return len(page.get("users", []))

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

    @staticmethod
    def breaking_news(page, wikidata):
        """
        Function that makes a binary decision on whether a page has breaking news value
        Based on: https://arxiv.org/abs/1303.4702

        :param page: Dictionary with page data
        :param wikidata: Dictionary with entity data
        :return: True if a page is breaking news, False if it isn't
        """

        revisions = page.get("revisions", [])
        if not len(revisions):
            return None

        # First we build "clusters" of revisions (aka edits) that happened 60 seconds from each other
        clusters = []
        revisions = iter(revisions)
        cluster_revisions = [next(revisions)]
        for revision in revisions:
            last_revision_timestamp = cluster_revisions[-1].get("timestamp")
            if revision.get("timestamp") - last_revision_timestamp > 60:
                if len(cluster_revisions) > 1:
                    clusters.append(cluster_revisions)
                cluster_revisions = [revision]
                continue
            cluster_revisions.append(revision)

        # Now we check the clusters for the breaking news quality defined as:
        # At least 5 concurrent revisions
        # At least 3 editors involved
        # One such cluster is sufficient to mark page as breaking news
        for cluster in clusters:
            if len(cluster) < 5:
                continue
            unique_editors = set([revision["user"] for revision in cluster])
            if len(unique_editors) >= 3:
                return True

        # No breaking news clusters
        return

    @staticmethod
    def all_alone(page, wikidata):
        """
        Function that makes a binary decision on whether a page was edited by a single editor

        :param page: Dictionary with page data
        :param wikidata: Dictionary with entity data
        :return: True if edits were made by a single person and False if they weren't
        """
        return len(page.get("users", [])) == 1

    @staticmethod
    def central_europe(page, wikidata):
        country_property = 'P17'
        central_europe_country_entities = [  # uses https://en.wikipedia.org/wiki/Central_Europe on 2017-07-14
            'Q40',  # Austria
            'Q224',  # Croatia
            'Q213',  # Czech Republic
            'Q183',  # Germany
            'Q28',  # Hungary
            'Q347'  # Liechtenstein
            'Q36',  # Poland
            'Q214',  # Slovakia
            'Q215',  # Slovenia
            'Q39',  # Switzerland

        ]
        return any(
            (claim["value"] for claim in wikidata.get("claims", [])
             if claim["property"] == country_property and
             claim["value"] in central_europe_country_entities)
        )

    @staticmethod
    def undo_and_rollback(page, wikidata):
        """
        Function to detect which pages received the most reverts
        Currently it only detects undo's and rollbacks. For more info on these actions:
        * https://en.wikipedia.org/wiki/Help:Reverting#Undo
        * https://en.wikipedia.org/wiki/Wikipedia:Rollback
        Detection is based on automated edit summaries: https://en.wikipedia.org/wiki/Help:Automatic_edit_summaries

        :param page: Dictionary with page data
        :param wikidata: Dictionary with entity data
        :return: The amount of undo's and rollbacks on a page by humans
        """
        revisions = page.get("revisions", [])
        if not len(revisions):
            return None

        revert_revisions = [
            revision for revision in revisions
            if "bot" not in revision["user"].lower() and
            (
                "Undid revision" in revision["comment"] or  # undo action on the history page
                "Reverted edits by" in revision["comment"]  # rollback action
            )
        ]
        return len(revert_revisions)
