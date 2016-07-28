from __future__ import unicode_literals, absolute_import, print_function, division

from collections import OrderedDict
from itertools import groupby
from datetime import datetime

from core.models.organisms import Community, Individual


class WikiNewsCommunity(Community):

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
                    "image": "$.pageprops.page_image",
                    "wikidata": "$.pageprops.wikibase_item"
                },
                "_concat_args_size": 50,
                "_continuation_limit": 1000,
                "_update_key": "pageid",
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
            },
            "schema": {},
            "errors": {},
        })
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

    def set_kernel(self):
        self.kernel = self.current_growth.output

    @property
    def manifestation(self):
        return list(super(WikiNewsCommunity, self).manifestation)[:20]

    class Meta:
        verbose_name = "Wiki news"
        verbose_name_plural = "Wiki news"
