from HIF.models import DataProcess
from HIF.input.http.google import GoogleImage
from HIF.input.http.wiki import WikiTranslate

class ImageTranslate(DataProcess):
    # Classes to combine
    translate_model = WikiTranslate
    image_model = GoogleImage

    def __init__(self, *args, **kwargs):
        super(ImageTranslate, self).__init__(*args, **kwargs)

    def process(self):
        pass
