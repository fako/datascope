import re

from collections import OrderedDict
from itertools import groupby, islice
from datetime import datetime

from django.conf import settings

from core.models.organisms import Community, Individual


class WikiFeedCommunity(Community):

    USER_AGENT = "WikiFeedBot (DataScope v{})".format(settings.DATASCOPE_VERSION)

    COMMUNITY_SPIRIT = OrderedDict([
        ("revisions", {
            "process": "HttpResourceProcessor.fetch",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective#pageid",
            "config": {
                "_args": [],
                "_kwargs": {},
                "_resource": "WikipediaRecentChanges",
                "_objective": {
                    "@": "$.query.recentchanges",
                    "pageid": "$.pageid",
                    "title": "$.title",
                    "timestamp": "$.timestamp",
                    "comment": "$.comment",
                    "userid": "$.userid"
                },
                "_continuation_limit": 1000,
                "user_agent": USER_AGENT
            },
            "schema": {},
            "errors": {},
        }),
        ("pages", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "Collective#pageid",  # gets filled by finish_revisions
            "contribute": "Update:ExtractProcessor.extract_from_resource",
            "output": "&input",
            "config": {
                "_args": ["$.pageid"],
                "_kwargs": {},
                "_resource": "WikipediaListPages",
                "_objective": {
                    "@": "$.query.pages",
                    "pageid": "$.pageid",
                    "title": "$.title",
                    "categories": "$.categories",
                    "image": "$.pageprops.page_image_free",
                    "wikidata": "$.pageprops.wikibase_item"
                },
                "_concat_args_size": 50,
                "_continuation_limit": 1000,
                "_update_key": "pageid",
                "user_agent": USER_AGENT
            },
            "schema": {},
            "errors": {},
        }),
        ("wikidata", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "Collective",  # gets a filter applied
            "contribute": "Inline:ExtractProcessor.extract_from_resource",
            "output": "@pages",
            "config": {
                "_args": ["$.wikidata"],
                "_kwargs": {},
                "_resource": "WikiDataItems",
                "_objective": {
                    "@": "$",
                    "wikidata": "$.id",
                    "claims": "$.claims",
                    "references": "$.references",
                    "description": "$.description",
                },
                "_inline_key": "wikidata",
                "_concat_args_size": 50,
                "_continuation_limit": 1000,
                "user_agent": USER_AGENT
            },
            "schema": {},
            "errors": {},
        }),
        # ("pageviews", {
        #     "process": "HttpResourceProcessor.fetch_mass",
        #     "input": "@wikidata",
        #     "contribute": "Update:ExtractProcessor.extract_from_resource",
        #     "output": "&input",
        #     "config": {
        #         "_args": ["$.title"],
        #         "_kwargs": {},
        #         "_resource": "WikipediaPageviewDetails",
        #         "_objective": {
        #             "@": "$.items",
        #             "title": "$.article",
        #             "pageviews": "$.views"
        #         },
        #         "_update_key": "title",
        #     },
        #     "schema": {},
        #     "errors": {},
        # })
    ])

    COMMUNITY_BODY = [
        {
            "process": "WikipediaRankProcessor.hooks",
            "config": {}
        }
    ]
    ASYNC_MANIFEST = True
    INPUT_THROUGH_PATH = False

    PUBLIC_CONFIG = {
        "$revision_count": 1,
        "$category_count": 1,
        "$number_of_deaths": 1,
        "$women": 1
    }

    def initial_input(self, *args):
        return Individual.objects.create(community=self, properties={}, schema={})

    def finish_revisions(self, out, err):
        pages_growth = self.next_growth()
        grouped_pages = groupby(out.individual_set.order_by("identity").iterator(), lambda ind: ind.identity)

        pages = []
        for pageid, revision_individuals in grouped_pages:
            # Filter mysterious pageids like None and "0"
            if not pageid:
                continue
            revisions = list(revision_individuals)
            pages.append({
                "pageid": pageid,
                "revisions": [revision.content for revision in revisions],
                "users": list({revision.properties["userid"] for revision in revisions if revision.properties["userid"]})
            })
            if len(pages) >= 1000:
                pages_growth.input.update(pages, reset=False)
                pages = []
        if len(pages):
            pages_growth.input.update(pages, reset=False)

    def begin_wikidata(self, inp):
        pages = self.growth_set.filter(type="pages").last().output
        pages.identifier = "wikidata"
        pages.save()
        now = datetime.now()
        pages.update(pages.content, reset=False, validate=False)
        pages.individual_set.filter(created_at__lt=now).delete()
        inp.update(pages.individual_set.filter(identity__isnull=False).exclude(identity="").iterator())

    def begin_pageviews(self, inp):
        inp.identifier = "title"
        inp.save()
        for individual in inp.individual_set.iterator():
            individual.clean()
            individual.save()

    def set_kernel(self):
        self.kernel = self.current_growth.output

    @property
    def manifestation(self):
        return islice(super(WikiFeedCommunity, self).manifestation, 20)

    class Meta:
        verbose_name = "Wiki feed"
        verbose_name_plural = "Wiki feeds"


class WikiFeedUsageCommunity(Community):

    USER_AGENT = "WikiFeedBot (DataScope v{})".format(settings.DATASCOPE_VERSION)

    COMMUNITY_SPIRIT = OrderedDict([
        ("transclusions", {
            "process": "HttpResourceProcessor.fetch",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective#title",
            "config": {
                "_args": ["$.page"],
                "_kwargs": {},
                "_resource": "WikipediaTransclusions",
                "_objective": {
                    "@": "$.query.pages",
                    "title": "$.title"
                },
                "_continuation_limit": 1000,
                "user_agent": USER_AGENT
            },
            "schema": {},
            "errors": {},
        }),
        ("revisions", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@transclusions",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective#title",
            "config": {
                "_args": ["$.title"],
                "_kwargs": {},
                "_resource": "WikipediaRevisions",
                "_objective": {
                    "@": "$.page.revisions",
                    "#namespace": "$.page.ns",
                    "#title": "$.page.title",
                    "user": "$.user",
                    "timestamp": "$.timestamp",
                    "revision": "$.*"
                },
                "_continuation_limit": 1000,
                "user_agent": USER_AGENT
            },
            "schema": {},
            "errors": {},
        })
    ])

    WIKI_FEED_TEMPLATE_REGEX = "\{\{User:Wiki[_\w]Feed[_\w]Bot/feed(?P<params>[|a-z0-9_=.\-]+)\}\}"

    def initial_input(self, *args):
        return Individual.objects.create(community=self, properties={"page": "User:Wiki_Feed_Bot/feed"}, schema={})

    def finish_revisions(self, out, err):
        pages = self.growth_set.filter(type="transclusions").last()
        for page in pages.output.individual_set.iterator():
            page["feed"] = None
            for revision in out.individual_set.filter(identity=page["title"]).iterator():

                # Basic validation for revision
                if revision["namespace"] != 2:
                    continue
                elif "User:" + revision["user"] != page["title"]:
                    continue
                elif page["feed"] is not None:
                    current_feed_time = datetime.strptime(page["feed"]["timestamp"][:-1], "%Y-%m-%dT%H:%M:%S")
                    revision_feed_time = datetime.strptime(revision["timestamp"][:-1], "%Y-%m-%dT%H:%M:%S")
                    if current_feed_time >= revision_feed_time:
                        continue

                # Extended validation and parsing of the template
                template_match = re.search(self.WIKI_FEED_TEMPLATE_REGEX, revision["revision"])
                if template_match is None:
                    print("no match")
                    continue
                template_params = template_match.group("params")
                template_params.replace(" ", "")
                template_params = template_params[1:].split("|")
                source = template_params.pop(0)
                module_params = (module.split("=") for module in template_params)
                modules = {module: float(weight) for module, weight in module_params}
                page["feed"] = {
                    "timestamp": revision["timestamp"],
                    "source": source,
                    "modules": modules
                }

            page.save()

    def set_kernel(self):
        self.kernel = self.growth_set.filter(type="transclusions").last().output

    class Meta:
        verbose_name = "Wiki feed usage"
        verbose_name_plural = "Wiki feed usages"
