from collections import OrderedDict

from core.models.organisms import Community
from core.utils.files import SemanticDirectoryScan


class InventoryCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("brands", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": None,
            "contribute": "Update:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["$.path"],
                "_kwargs": {},
                "_resource": "BrandPrediction",
                "_objective": {
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
        collective = self.create_organism("Collective", schema={})
        scanner = SemanticDirectoryScan(file_pattern="*f.jpg")
        content = []
        for file_data in scanner("system/files/media/Pilot"):
            store, year, id_ = file_data["name"].split("_")
            file_data.update({
                "store": store,
                "year": int(year),
                "id": int(id_)
            })
            content.append(file_data)
        collective.update(content)
        return collective
