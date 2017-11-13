import dateutil.parser
import datetime

from core.processors.rank import RankProcessor


def users_watch(users, page_data):
    """
    For tracking edits from particular IP ranges or Usernames

    :param users: list of usernames or ips to watch out for
    :param page_data: page data passed into characteristic function
    :return: count of watched users/ips found in page data
    """
    users = set(users)
    page_users = page_data.get("users", [])
    return len([
        user for user in page_users
        if user in users
    ])


def categories_watch(categories, page_data):
    """
    For tracking given list of categories

    :param categories: list of category titles to watch out for
    :param page_data: page data passed into characteristic function
    :return: count of watched categories found in page data
    """
    categories = set(categories)
    page_categories = [category["title"] for category in page_data.get("categories", [])]
    return len([
        category for category in page_categories
        if category in categories
    ])


def claim_watch(property, item, wikidata):
    """
    For tracking wikidata claims of articles
    
    :param property: the WikiData property code to watch
    :param item: the WikiData item code the property should match
    :param wikidata: wikidata data passed into characteristic function
    :return: Boolean indicating if claim (property = item) is inside wikidata of article
    """
    return any(
        (claim for claim in wikidata.get("claims", [])
        if claim["property"] == property and claim["value"] == item)
    )


def claim_exists(property, wikidata):
    """
    For tracking if a particular property is set

    :param property: the WikiData property code to watch
    :param wikidata: wikidata data passed into characteristic function
    :return: Boolean indicating if propery occurs
    """
    return any(
        (claim for claim in wikidata.get("claims", [])
         if claim["property"] == property)
    )


def get_quantity(property, wikidata):
    """
    For tracking quantities in wikidata

    :param property: the WikiData property code to watch (should have a quantity as data)
    :param wikidata: wikidata data passed into characteristic function
    :return: Float that is the value of the quantity of the specified property 
    """
    return next(
        (float(claim["value"]["amount"]) for claim in wikidata.get("claims", [])
        if claim["property"] == property)
    , 0.0)


def get_time(property, wikidata):
    """
    For tracking time in wikidata

    :param property: the WikiData property code to watch (should have time as data)
    :param wikidata: wikidata data passed into characteristic function
    :return: Timestamp that is the value of the time of the specified property
    """
    return next(
        (dateutil.parser.parse(claim["value"]["time"]) for claim in wikidata.get("claims", [])
         if claim["property"] == property)
    , 0.0)


class WikipediaRankProcessor(RankProcessor):
    def get_hook_arguments(self, individual):
        individual_argument = super(WikipediaRankProcessor, self).get_hook_arguments(individual)[0]
        wikidata_argument = individual_argument.get("wikidata", {})
        if wikidata_argument is None or isinstance(wikidata_argument, str):
            wikidata_argument = {}
        return [individual_argument, wikidata_argument]

    @staticmethod
    def politician_scandals(page, wikidata):
        is_scandal = claim_watch("P31", "Q192909", wikidata) > 0
        # What I *really* want to query is scandals that IMPLICATE politicians
        involves_politician = claim_watch("P425", "Q7163", wikidata) > 0
        return (1 if is_scandal or involves_politician else 0) * WikipediaRankProcessor.edit_count(page, wikidata)

    @staticmethod
    def political_organising(page, wikidata):
        is_civil_society_campaign = claim_watch("P31", "Q5124698", wikidata) > 0 # has 0 entries
        is_political_campaign = claim_watch("P31", "Q847301", wikidata) > 0
        return (1 if is_civil_society_campaign or is_political_campaign else 0) * WikipediaRankProcessor.edit_count(
            page, wikidata)

    @staticmethod
    def investigative_journalism(page, wikidata):
        return claim_watch("P31","Q366",wikidata)

    @staticmethod
    def edit_count(page, wikidata):
        return len(page.get("revisions", []))

    @staticmethod
    def most_viewed_books(page, wikidata):
        return claim_watch("P31", "Q571", wikidata=wikidata) * page.get("pageviews", 0)

    @staticmethod
    def category_count(page, wikidata):
        return len(page.get("categories", []))

    @staticmethod
    def editor_count(page, wikidata):
        return len(page.get("users", []))

    @staticmethod
    def number_of_deaths(page, wikidata):
        number_of_deaths_property = "P1120"
        return int(get_quantity(number_of_deaths_property, wikidata))

    @staticmethod
    def is_woman(page, wikidata):
        sex_property = "P21"
        women_item = "Q6581072"
        return any(
            (claim for claim in wikidata.get("claims", [])
            if claim["property"] == sex_property and claim["value"] == women_item)
        )

    @staticmethod
    def london_traffic_accidents(page, wikidata):
      is_traffic_accident = claim_watch("P31", "Q9687", wikidata=wikidata)
      is_in_greater_london = claim_watch("P131", "Q23306", wikidata=wikidata)
      num_deaths = get_quantity("P1120", wikidata)
      return (is_traffic_accident * is_in_greater_london) * (1 + num_deaths)

    @staticmethod
    def chicago_homicides(page, wikidata):
      is_homicide = claim_watch("P31", "Q149086", wikidata=wikidata)
      is_in_chicago = claim_watch("P131", "Q1297", wikidata=wikidata)
      num_deaths = get_quantity("P1120", wikidata)
      return (is_homicide * is_in_chicago) * (1 + num_deaths)

    @staticmethod
    def box_office(page, wikidata):
        box_office_property = "P2142"
        return get_quantity(box_office_property, wikidata)

    @staticmethod
    def is_superhero_film(page, wikidata):
        return claim_watch("P136", "Q1535153", wikidata=wikidata)

    @staticmethod
    def superhero_blockbusters(page, wikidata):
        is_superhero_film = claim_watch(
            "P136",              # genre
            "Q1535153",          # superhero film
            wikidata=wikidata
        )
        box_office = get_quantity(
            "P2142",             # box office
            wikidata=wikidata
        )
        return is_superhero_film * box_office
    
    @staticmethod
    def football_stadia_by_size(page, wikidata):
        is_stadium = claim_watch("P31",        # instance of
                                 "Q1154710",   # football stadium
                                 wikidata=wikidata)
        max_capacity = get_quantity("P1083",   # maximum capacity
                                    wikidata=wikidata)
        return is_stadium * max_capacity

    @staticmethod
    def whats_on_tv(page, wikidata):
        is_on_tv = claim_exists("P3301",       # broadcast by
                                 wikidata=wikidata)
        event_date = get_time("P585",          # point in time
                              wikidata=wikidata)
        day_diff = (event_date - datetime.date.today()).days
        
        if day_diff <= 0:
            return 0
        else:
            return is_on_tv / (0.2 + day_diff)

    @staticmethod
    def many_concurrent_editors(page, wikidata):
        """
        Function that makes a binary decision on whether a page has breaking news value
        Based on: https://arxiv.org/abs/1303.4702

        :param page: Dictionary with page data
        :param wikidata: Dictionary with entity data
        :return: True if a page is breaking news, False if it isn't
        """
        revisions = sorted(
            page.get("revisions", []),
            key=lambda rev: rev["timestamp"]
        )
        if not len(revisions):
            return None

        # First we build "clusters" of revisions (aka edits) that happened 60 seconds from each other
        clusters = []
        revisions = iter(revisions)
        cluster_revisions = [next(revisions)]
        for revision in revisions:
            last_revision_timestamp = cluster_revisions[-1].get("timestamp")
            between_revisions = dateutil.parser.parse(revision.get("timestamp")) - \
                                dateutil.parser.parse(last_revision_timestamp)
            if between_revisions.seconds >= 60:
                if len(cluster_revisions) > 1:
                    clusters.append(cluster_revisions)
                cluster_revisions = [revision]
                continue
            cluster_revisions.append(revision)

        # Now we check the clusters for the breaking news quality defined as:
        # At least 3 concurrent revisions (paper suggests 5, but that is cross language and we only look at English)
        # At least 3 editors involved
        # One such cluster is sufficient to mark page as breaking news
        for cluster in clusters:
            if len(cluster) < 3:
                continue
            unique_editors = set([revision["user"] for revision in cluster])
            if len(unique_editors) >= 3:
                return True

        # No breaking news clusters
        return

    @staticmethod
    def single_editor(page, wikidata):
        """
        Function that makes a binary decision on whether a page was edited by a single editor

        :param page: Dictionary with page data
        :param wikidata: Dictionary with entity data
        :return: True if edits were made by a single person and False if they weren't
        """
        return len(page.get("users", [])) == 1

    @staticmethod
    def central_europe(page, wikidata):
        """
        Function that makes a binary decision on whether a page has a location that lies in Central Europe.

        :param page: Dictionary with page data
        :param wikidata: Dictionary with entity data
        :return: True if the page contains a country property that is set to a country in Central Europe
        """
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
            if revision["user"] and "bot" not in revision["user"].lower() and
            (
                "Undid revision" in revision["comment"] or  # undo action on the history page
                "Reverted edits by" in revision["comment"]  # rollback action
            )
        ]
        return len(revert_revisions)
