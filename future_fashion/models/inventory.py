import os
import shutil
from collections import OrderedDict

from django.core.files.storage import default_storage

from core.models.organisms import Community
from core.utils.files import SemanticDirectoryScan
from future_fashion.colors import extract_dominant_colors, create_colors_data


class InventoryCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("brands", {
            "process": "HttpResourceProcessor.submit_mass",
            "input": None,
            "contribute": "Update:ExtractProcessor.extract_from_resource",
            "output": "&input",
            "config": {
                "_args": [],
                "_kwargs": {"image": "$.path"},
                "_resource": "BrandRecognitionService",
                "_objective": {
                    "@": "$",
                    "path": "$.path",
                    "brand": "$.results.prediction",
                    "confidence": "$.results.confidence"
                },
                "_update_key": "path"
            },
            "schema": {},
            "errors": {},
        })
    ])

    def initial_input(self, *args):
        collective = self.create_organism("Collective", schema={}, identifier="path")
        scanner = SemanticDirectoryScan(file_pattern="*f.jpg")
        content = []
        for file_data in scanner("system/files/media/Pilot"):
            color_data = {}
            for num_colors in [2, 3, 6]:
                colors, balance = extract_dominant_colors(file_data["path"], num=num_colors)
                color_data.update(create_colors_data(colors, balance))
            store, year, id_, view = file_data["name"].split("_")
            file_data.update({
                "store": store,
                "year": int(year),
                "id": int(id_),
                "colors": color_data
            })
            content.append(file_data)
        collective.update(content)
        return collective

    def finish_brands(self, out, err):
        items = list(out.content)
        items.sort(key=lambda item: item["confidence"], reverse=True)
        for item in items[:20]:
            dest = os.path.join(default_storage.location, "inventory", "branded", item["brand"])
            if not os.path.exists(dest):
                os.makedirs(dest)
            shutil.copy2(item["path"], os.path.join(dest, item["file"]))

    def set_kernel(self):
        self.kernel = self.get_growth("brands").output

    class Meta:
        verbose_name = "Inventory community"
        verbose_name_plural = "Inventory communities"
