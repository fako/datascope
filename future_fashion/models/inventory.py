from collections import OrderedDict

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

    def initial_input(self, *args):
        collective = self.create_organism("Collective", schema={}, identifier="path")
        scanner = SemanticDirectoryScan(file_pattern="*f.jpg")
        content = []
        for file_data in scanner("system/files/media/Pilot"):
            store, year, id_, view = file_data["name"].split("_")
            file_data.update({
                "store": store,
                "year": int(year),
                "id": int(id_)
            })
            content.append(file_data)
        collective.update(content)
        return collective

    def set_kernel(self):
        self.kernel = self.get_growth("brands").output

    class Meta:
        verbose_name = "Inventory community"
        verbose_name_plural = "Inventory communities"
