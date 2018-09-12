import os
from collections import OrderedDict

from django.core.exceptions import ValidationError

from core.models.organisms import Community
from core.utils.files import SemanticDirectoryScan
from future_fashion.colors import extract_dominant_colors, create_colors_data


class ClothingInventoryCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("types", {
            "process": "HttpResourceProcessor.submit_mass",
            "input": None,
            "contribute": "Update:ExtractProcessor.extract_from_resource",
            "output": "&input",
            "config": {
                "_args": [],
                "_kwargs": {"image": "$.path"},
                "_resource": "ClothingTypeRecognitionService",
                "_objective": {
                    "@": "$",
                    "path": "$.path",
                    "type": "$.results.prediction",
                    "confidence": "$.results.confidence"
                },
                "_update_key": "path"
            },
            "schema": {},
            "errors": {},
        })
    ])

    COMMUNITY_BODY = [
        {
            "name": "color_and_type_match",
            "process": "ClothingSetMatchProcessor.color_and_type",
            "config": {
                "type_limit": 10,
                "$top": None,
                "$bottom": None,
                "$accessories": None
            }
        }
    ]

    def initial_input(self, *args):
        collective = self.create_organism("Collective", schema={}, identifier="path")
        scanner = SemanticDirectoryScan(file_pattern="*f.jpg", progress_bar=True)
        content = []
        target_directory = os.path.join("future_fashion", "data", "media", "future_fashion", args[0])
        if not os.path.exists(target_directory):
            raise ValidationError("Directory {} does not exist".format(target_directory))
        for file_data in scanner(target_directory):
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

    def set_kernel(self):
        self.kernel = self.get_growth("types").output

    def get_clothing_frame_file(self):
        return os.path.join(self._meta.app_label, "data", "clothing_frames", self.signature + ".pkl")

    def before_color_and_type_match_manifestation(self, manifestation_part):
        manifestation_part["config"]["clothing_frame_path"] = self.get_clothing_frame_file()

    class Meta:
        verbose_name = "Clothing inventory community"
        verbose_name_plural = "Clothing inventory communities"
