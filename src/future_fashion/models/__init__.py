from .data import ClothingDataCommunity
from .sources.recognition import BrandRecognitionService, ClothingTypeRecognitionService
from .sources.files import ClothingImageDownload
from .inventory import ClothingInventoryCommunity
from .clothing_sets import ColorClothingSet, ColorClothingSetSerializer
from .storage import Collection, Document
from .annotation import Annotation


class ImageFeatures(object):
    pass
