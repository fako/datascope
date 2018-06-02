from core.models.resources import MicroServiceResource


class ImageRecognitionService(MicroServiceResource):

    MICRO_SERVICE = "image_recognition"

    @property
    def content(self):
        mime_type, data = super().content
        data["confidence"] = data["probabilities"][data["prediction"]]
        vars = self.variables()
        return mime_type, {
            "path": vars["path"],
            "results": data
        }

    def variables(self, *args):
        args = args or self.request.get("args")
        return {
            "path": args[0]
        }

    class Meta:
        abstract = True
