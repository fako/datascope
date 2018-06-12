import os
import shutil
import itertools
from collections import OrderedDict
from operator import itemgetter

import pandas as pd
from colorz import colorz

from django.core.files.storage import default_storage

from core.models.organisms import Community
from core.utils.files import SemanticDirectoryScan


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

    def get_main_colors_from_file(self, file_path):
        return list(map(itemgetter(0), colorz(file_path)))  #, min_v=0, max_v=255)))

    def initial_input(self, *args):
        collective = self.create_organism("Collective", schema={}, identifier="path")
        scanner = SemanticDirectoryScan(file_pattern="*f.jpg")
        content = []
        for file_data in scanner("system/files/media/Pilot"):
            colors = self.get_main_colors_from_file(file_data["path"])
            store, year, id_, view = file_data["name"].split("_")
            file_data.update({
                "store": store,
                "year": int(year),
                "id": int(id_),
                "colors": colors
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

    def get_vector_from_colors(self, colors):
        return list(itertools.chain(*colors))

    def get_colors_frame(self):
        records = [self.get_vector_from_colors(ind["colors"]) for ind in self.kernel.content]
        num_colors = int(len(records[0])/3)
        labels = []
        for ix in range(num_colors):
            ix = str(ix)
            labels += ["r"+ix, "g"+ix, "b"+ix]
        return pd.DataFrame.from_records(records, columns=labels)

    class Meta:
        verbose_name = "Inventory community"
        verbose_name_plural = "Inventory communities"
