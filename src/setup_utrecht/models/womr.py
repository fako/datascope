import os
import shutil
from collections import OrderedDict

from django.core.files.storage import default_storage

from core.models.organisms import Community, Collective, Individual
from sources.models import ImageDownload


class UniformImagesCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("images", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["$.word", "$.country", "$.image_quantity"],
                "_kwargs": {},
                "_resource": "sources.GoogleImage",
                "_objective": {
                    "@": "$.items",
                    "#word": "$.queries.request.0.searchTerms",
                    "url": "$.link",
                    "width": "$.image.width",
                    "height": "$.image.height",
                    "thumbnail": "$.image.thumbnailLink",
                },
                "_continuation_limit": 1000,
                "_interval_duration": 1000
            },
            "schema": {},
            "errors": {},
        }),
        ("download", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@images",
            "contribute": None,
            "output": "&input",
            "config": {
                "_args": ["$.url", "$.word"],
                "_kwargs": {},
                "_resource": "setup_utrecht.UniformImageDownload"
            },
            "schema": {},
            "errors": None,
        })
    ])

    COMMUNITY_BODY = []

    def initial_input(self, *args):
        collective = Collective.objects.create(community=self, schema={})
        for arg in args:
            Individual.objects.create(
                community=self,
                collective=collective,
                properties={
                    "word": arg,
                    "country": "countryNL",
                    "image_quantity": 300
                }
            )
        return collective

    def set_kernel(self):
        self.kernel = self.get_growth("images").output

    def finish_download(self, out, err):
        for individual in out.individual_set.iterator():
            image_uri = ImageDownload.uri_from_url(individual["url"])
            try:
                download = ImageDownload.objects.get(uri=image_uri)
            except ImageDownload.DoesNotExist:
                continue
            if not download.success:
                continue
            os.makedirs(os.path.join(
                default_storage.location,
                self.signature,
                individual["word"]
            ), exist_ok=True)
            shutil.copy2(
                os.path.join(default_storage.location, download.body),
                os.path.join(default_storage.location, self.signature, individual["word"])
            )

    class Meta:
        verbose_name = "Uniform images community"
        verbose_name_plural = "Uniform images communities"
