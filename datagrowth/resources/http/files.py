import os
from io import BytesIO
import hashlib
from PIL import Image
from urlobject import URLObject
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files import File
from django.core.files.images import ImageFile

from datagrowth import settings as datagrowth_settings
from datagrowth.resources.http.generic import HttpResource


class HttpFileResource(HttpResource):  # TODO: write tests

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string",
                    "pattern": "^http"
                }
            ],
            "minItems": 1,
            "additionalItems": False
        }
    }

    def variables(self, *args):
        args = args or self.request.get("args")
        return {
            "url": args[0]
        }

    def _send(self):
        if self.request["cancel"]:
            return
        super()._send()

    def _create_request(self, method, *args, **kwargs):
        cancel_request = False
        variables = self.variables(*args)
        try:
            self._validate_input("get", *args, **kwargs)
        except ValidationError as exc:
            if variables["url"].startswith("http"):
                raise exc
            # Wrong protocol given, like: x-raw-image://
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

    def _get_file_class(self):
        return File

    def _get_file_info(self, url):
        # Getting the file name and extension from url
        path = str(URLObject(url).path)
        tail, head = os.path.split(path)
        name, extension = os.path.splitext(head)
        now = datetime.utcnow()
        file_name = "{}.{}".format(
            now.strftime(datagrowth_settings.DATAGROWTH_DATETIME_FORMAT),
            name
        )
        # Hashing the file name
        hasher = hashlib.md5()
        hasher.update(file_name.encode('utf-8'))
        file_hash = hasher.hexdigest()
        # Constructing file path
        file_path = os.path.join(
            datagrowth_settings.DATAGROWTH_MEDIA_ROOT,
            self._meta.app_label,
            "downloads",
            file_hash[0], file_hash[1:3]  # this prevents huge (problematic) directory listings
        )
        return file_path, file_name, extension

    def _save_file(self, url, content):
        file_path, file_name, extension = self._get_file_info(url)
        if len(file_name) > 150:
            file_name = file_name[:150]
        file_name += extension
        if len(file_name) > 155:
            file_name = file_name[:155]
        FileClass = self._get_file_class()
        file = FileClass(BytesIO(content))
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_name = default_storage.save(os.path.join(file_path, file_name), file)
        return file_name

    def _update_from_response(self, response):
        file_name = self._save_file(self.request["url"], response.content)
        self.head = dict(response.headers)
        self.status = response.status_code
        self.body = file_name.replace(datagrowth_settings.DATAGROWTH_MEDIA_ROOT, "").lstrip("/")

    def transform(self, file):
        return file

    @property
    def content(self):
        if self.success:
            content_type = self.head.get("content-type", "unknown/unknown").split(';')[0]
            file_path = os.path.join(default_storage.location, self.body)
            file = default_storage.open(file_path)
            try:
                return content_type, self.transform(file)
            except IOError:
                return None, None
        return None, None

    def post(self, *args, **kwargs):
        raise NotImplementedError("You can't download an image over POST")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = kwargs.get("timeout", 4)

    class Meta:
        abstract = True


class HttpImageResource(HttpFileResource):

    def _get_file_class(self):
        return ImageFile

    def transform(self, file):
        return Image.open(file)

    class Meta:
        abstract = True
