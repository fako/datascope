from __future__ import unicode_literals, absolute_import, print_function, division
import six

from collections import OrderedDict

from core.models.organisms import Community, Individual


class WikiNewsCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("revisions", {
            "process": "HttpResourceProcessor.fetch",
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
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "errors": {},
            "schema": {},
            "output": "Collective",
        })
    ])

    def initial_input(self, *args, **kwargs):
        return Individual.objects.create(community=self, properties={}, schema={})

    def finish_revisions(self, out, err):
        pages = {}
        deletes = []
        for ind in out.individual_set.all():
            if ind.properties["pageid"] not in pages:
                pages[ind.properties["pageid"]] = ind
                ind.properties = {
                    "pageid": ind.properties["pageid"],
                    "revisions": [ind.content]
                }
            else:
                pages[ind.properties["pageid"]]["revisions"].append(ind.content)
                deletes.append(ind.id)
        out.individual_set.all().delete()
        out.individual_set.bulk_create(six.itervalues(pages))

    def set_kernel(self):
        self.kernel = self.current_growth.output
