from datagrowth.resources import HttpImageResource
from core.utils.files import FileSorter, MissingFileSource


class ImageDownload(HttpImageResource):
    pass


class ImageDownloadSorter(FileSorter):

    def __init__(self, source_base, destination_base, url_key, destination_lambda):
        super().__init__(source_base, destination_base)
        self.url_key = url_key
        self.destination_lambda = destination_lambda

    def get_source(self, file_data):
        url = file_data.get(self.url_key)
        uri = ImageDownload.uri_from_url(url)
        try:
            download = ImageDownload.objects.get(uri=uri)
        except ImageDownload.DoesNotExist:
            raise MissingFileSource("ImageDownload does not exist")
        if not download.success:
            raise MissingFileSource("ImageDownload failed")
        return download.body

    def get_destination(self, file_data):
        return self.destination_lambda(file_data)
