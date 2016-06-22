from __future__ import unicode_literals, absolute_import, print_function, division
import six

from django.conf import settings
from django.core.files.storage import default_storage

from collections import OrderedDict

from core.models.organisms import Community, Collective, Individual


class FutureFashionCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("vectors", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": None,
            "contribute": "Update:ExtractProcessor.pass_resource_through",
            "output": "&input",  # same as initial_input
            "config": {
                "_args": ["$.file"],
                "_kwargs": {},
                "_resource": "ImageFeatures",
                "_update_key": "file"
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
        directory = args[0]
        initial = Collective.objects.create(community=self, schema={})
        directories, files = default_storage.listdir(directory)
        for file in files:
            full_name = directory + '/' + file
            size = default_storage.size(full_name)
            if size < 3 * 1024:
                continue

            properties = {
                "size": size,
                "name": file,
                "file": default_storage.path(full_name),
                "url": default_storage.url(full_name)
            }
            Individual.objects.create(community=self, collective=initial, properties=properties, schema={})
        return initial

    def set_kernel(self):
        self.kernel = self.current_growth.output

    @property
    def manifestation(self):
        return list(super(FutureFashionCommunity, self).manifestation)[:20]

    class Meta:
        verbose_name = "Future fashion"
        verbose_name_plural = "Future fashions"
