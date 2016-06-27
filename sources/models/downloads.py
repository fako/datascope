from __future__ import unicode_literals, absolute_import, print_function, division
from six import BytesIO

from PIL import Image
from urlobject import URLObject
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.images import ImageFile
from django.conf import settings

from core.models.resources.http import HttpResource


class ImageDownload(HttpResource):  # TODO: write tests

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string",
                    "pattern": "^http"
                },
                {
                    "type": "string"
                }
            ],
            "minItems": 1,
            "additionalItems": False
        }
    }

    def variables(self, *args):
        args = args or self.request.get("args")
        return {
            "url": args[0],
            "prefix": args[1] + "." if len(args) > 1 else ""
        }

    def _send(self):
        if self.request["cancel"]:
            return
        super(ImageDownload, self)._send()

    def _create_request(self, method, *args, **kwargs):
        cancel_request = False
        variables = self.variables(*args)
        try:
            self._validate_input("get", *args, **kwargs)
        except ValidationError as exc:
            if variables["url"].startswith("http"):
                raise exc
            # Wrong URL given
            self.set_error(404)
            cancel_request = True
        return self.validate_request({
            "args": args,
            "kwargs": kwargs,
            "method": "get",
            "url": variables["url"],
            "headers": {},
            "data": None,
            "cancel": cancel_request
        }, validate_input=False)

    def _save_image(self, url, content):
        path = str(URLObject(url).path)
        file_name_position = path.rfind('/') + 1
        extension_position = path.rfind('.') + 1
        assert file_name_position >= 1, "Can't determine file name for {}".format(url)
        variables = self.variables()
        now = datetime.utcnow()
        file_name = "{}.{}{}".format(
            now.strftime(settings.DATASCOPE_DATETIME_FORMAT),
            variables["prefix"],
            path[file_name_position:]
        )
        if len(file_name) > 150:
            file_name = file_name[:150] + '.' + path[extension_position:]
        image = ImageFile(BytesIO(content))
        image_name = default_storage.save('downloads/' + file_name, image)
        return image_name

    def _update_from_response(self, response):
        image_name = self._save_image(self.request["url"], response.content)
        self.head = dict(response.headers)
        self.status = response.status_code
        self.body = image_name

    @property
    def content(self):
        if self.success:
            content_type = self.head.get("content-type", "unknown/unknown").split(';')[0]
            image_file = default_storage.open(self.body)
            try:
                return content_type, Image.open(image_file)
            except IOError:
                return None, None
        return None, None

    def post(self, *args, **kwargs):
        raise NotImplementedError("You can't download an image over POST")

    def __init__(self, *args, **kwargs):
        super(ImageDownload, self).__init__(*args, **kwargs)
        self.timeout = kwargs.get("timeout", 4)
