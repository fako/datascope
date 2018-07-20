from sources.models import ImageRecognitionService


class BrandRecognitionService(ImageRecognitionService):
    pass


class ClothingTypeRecognitionService(ImageRecognitionService):
    MICRO_SERVICE = "clothing_type_recognition"
