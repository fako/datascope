from core.models.resources.http import HttpResource

from PIL import Image
from StringIO import StringIO


class ImageDownload(HttpResource):

    def _validate_input(self, method, *args, **kwargs):
        # TODO: validate for valid URL in args[0]. Use GET_SCHEMA?
        pass

    def _create_request(self, method, *args, **kwargs):
        self._validate_input("get", *args, **kwargs)
        return self.validate_request({
            "args": [],
            "kwargs": {},
            "method": "get",
            "url": args[0],
            "headers": {},
            "data": None,
        }, validate_input=False)

    def _update_from_response(self, response):
        self.head = dict(response.headers)
        self.status = response.status_code
        self.body = response.content

    @property
    def content(self):
        if self.success:
            content_type = self.head["content-type"].split(';')[0]
            return content_type, Image.open(StringIO(self.body))
        return None, None

    def post(self, *args, **kwargs):
        raise NotImplementedError("You can't download an image over POST")