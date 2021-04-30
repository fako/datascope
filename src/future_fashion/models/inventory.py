import os
from collections import OrderedDict

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError

from datagrowth import settings as datagrowth_settings
from datagrowth.utils import get_model_path, get_media_path
from core.models.organisms import Community
from core.utils.files import SemanticDirectoryScan
from future_fashion.colors import (extract_dominant_colors, create_colors_data, remove_white_image_background,
                                   brighten as colorz_brighten)
from future_fashion.models.storage import Document, Collection


class ClothingInventoryCommunity(Community):

    collection_set = GenericRelation(Collection, content_type_field="community_type", object_id_field="community_id")
    document_set = GenericRelation(Document, content_type_field="community_type", object_id_field="community_id")

    @property
    def collections(self):
        return self.collection_set

    @property
    def documents(self):
        return self.document_set

    COMMUNITY_SPIRIT = OrderedDict([
        ("types", {
            "process": "HttpResourceProcessor.submit_mass",
            "input": None,
            "contribute": "Update:ExtractProcessor.extract_from_resource",
            "output": "&input",
            "config": {
                "_args": [],
                "_kwargs": {"image": "$.path"},
                "_resource": "future_fashion.ClothingTypeRecognitionService",
                "_objective": {
                    "@": "$",
                    "path": "$.path",
                    "type": "$.results.prediction",
                    "confidence": "$.results.confidence"
                },
                "_update_key": "path",
                # TODO: below configs should be set by image processor stage, they are not used by "types"
                "$brighten": 0,
                "$remove_background": False
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
                "$bottom": None
            }
        }
    ]

    DATAGROWTH = True

    ANNOTATIONS = [
        {
            "name": "clothing_type",
            "type": "enum",
            "symbols": [
                "t_shirt",
                "top",
                "shorts",
                "trousers",
                "jeans",
                "skirt",
                "dress",
                "summer_jacket",
                "coat",
                "suit",
                "waistcoat",
                "sweater",
                "cardigan",
                "shirt",
                "leggings",
                "shoes",
                "hat",
                "bag",
                "glasses",
                "shawl",
                "necklace",
                "other"
            ]
        }
    ]

    def initial_input(self, *args):
        collection = self.create_organism("Collection", identifier="path", referee="rid")
        scanner = SemanticDirectoryScan(file_pattern="*f.jpg", progress_bar=True)
        content = []
        target_directory = get_media_path(self._meta.app_label, args[0])
        relative_media_directory = get_media_path(self._meta.app_label, args[0], absolute=False)
        if not os.path.exists(target_directory):
            raise ValidationError("Directory {} does not exist".format(target_directory))
        brighten = int(self.config.get("brighten", 0))
        remove_background = self.config.get("remove_background", False)
        for file_data in scanner(target_directory, path_prefix=relative_media_directory + os.sep):
            color_data = {}
            file_path = os.path.join(datagrowth_settings.DATAGROWTH_MEDIA_ROOT, file_data["path"])
            img = remove_white_image_background(file_path) if remove_background else file_path
            for num_colors in [2, 3, 6]:
                colors, balance = extract_dominant_colors(img, num=num_colors)
                if brighten:
                    colors = [list(colorz_brighten(color, brighten)) for color in colors]
                color_data.update(create_colors_data(colors, balance))
            store, year, id_, view = file_data["name"].split("_")
            file_data.update({
                "store": store,
                "year": int(year),
                "rid": "_".join([store, year, id_]),
                "colors": color_data
            })
            content.append(file_data)
        collection.add(content)
        return collection

    def set_kernel(self):
        self.kernel = self.get_growth("types").output
        super().set_kernel()

    def get_clothing_frame_file(self):
        return os.path.join(
            get_model_path(self._meta.app_label , "clothing_frames"),
            self.signature + ".pkl"
        )

    def before_color_and_type_match_manifestation(self, manifestation_part):
        manifestation_part["config"]["clothing_frame_path"] = self.get_clothing_frame_file()

    class Meta:
        verbose_name = "Clothing inventory community"
        verbose_name_plural = "Clothing inventory communities"
