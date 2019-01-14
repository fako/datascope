from core.models.resources import MicroServiceResource


class ImageRecognitionService(MicroServiceResource):

    MICRO_SERVICE = "image_recognition"
    FILE_DATA_KEYS = ["image"]

    @property
    def content(self):
        mime_type, data = super().content
        if not self.success:
            return mime_type, data

        data["confidence"] = data["probabilities"][data["prediction"]]
        return mime_type, [{
            "path": self.request["kwargs"].get("image"),
            "results": data
        }]

    class Meta:
        abstract = True
