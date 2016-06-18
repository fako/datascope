from __future__ import unicode_literals, absolute_import, print_function, division
import six

from django.conf import settings

from collections import OrderedDict

from core.models.organisms import Community, Individual


class FutureFashionCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("vectors", {
            "process": "HttpResourceProcessor.fetch",
            "input": None,
            "contribute": "Inline:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": [],
                "_kwargs": {},
                "_resource": "",
                "_objective": {
                },
                "_inline_key": "vectors"
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
        "$euclidean_distance": 1
    }

    def initial_input(self, *args):
        return Individual.objects.create(community=self, properties={}, schema={})

    def set_kernel(self):
        self.kernel = self.current_growth.output

    @property
    def manifestation(self):
        return list(super(FutureFashionCommunity, self).manifestation)[:20]

    class Meta:
        verbose_name = "Future fashion"
        verbose_name_plural = "Future fashions"
