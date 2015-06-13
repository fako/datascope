from __future__ import unicode_literals, absolute_import, print_function, division
import six

from django.conf import settings

from collections import OrderedDict

from core.models.organisms import Community, Individual


class WikiNewsCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("revisions", {
            "process": "HttpResourceProcessor.fetch",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": [],
                "_kwargs": {},
                "_resource": "WikipediaRecentChanges",
                "_objective": {
                    "@": "$.query.recentchanges",
                    "pageid": "$.pageid",
                    "title": "$.title",
                    "timestamp": "$.timestamp",
                    "comment": "$.comment"
                },
                "_continuation_limit": 1000,
            },
            "schema": {},
            "errors": {},
        }),
        ("pages", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@revisions",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
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

    PUBLIC_CONFIG = {
        "$revision_count": 1,
        "$category_count": 1,
    }

    def initial_input(self, *args, **kwargs):
        return Individual.objects.create(community=self, properties={}, schema={})

    def finish_revisions(self, out, err):
        pages = {}
        for ind in out.individual_set.all():
            if ind.properties["pageid"] not in pages:
                pages[ind.properties["pageid"]] = ind
                ind.properties = {
                    "pageid": ind.properties["pageid"],
                    "revisions": [ind.content]
                }
            else:
                pages[ind.properties["pageid"]]["revisions"].append(ind.content)
        out.individual_set.all().delete()
        out.individual_set.bulk_create(six.itervalues(pages), batch_size=settings.MAX_BATCH_SIZE)

    def finish_pages(self, out, err):
        pages = {}
        for ind in out.individual_set.all():
            if ind.properties["pageid"] not in pages:
                pages[ind.properties["pageid"]] = ind
                if ind.properties["categories"] is None:
                    ind.properties["categories"] = []
            else:
                if "categories" in ind.properties and ind.properties["categories"]:
                    pages[ind.properties["pageid"]].properties["categories"] += ind.properties["categories"]

        revisions = self.growth_set.filter(type="revisions").last().output
        for page in revisions.individual_set.all():
            try:
                pages[page.properties["pageid"]].properties.update(page.properties)
            except KeyError:
                print("KeyError:", page.properties["pageid"])

        out.individual_set.all().delete()
        out.individual_set.bulk_create(six.itervalues(pages), batch_size=settings.MAX_BATCH_SIZE)

    def set_kernel(self):
        self.kernel = self.current_growth.output

    @property
    def manifestation(self):
        return super(WikiNewsCommunity, self).manifestation[:20]
