import re
import hashlib
from copy import copy


class WikipediaImagesMixin(object):

    @property
    def content(self):
        if not self._json_body:
            # We're gonna make some hackish changes to the raw response
            original_body = copy(self.body)
            # Replace image references with absolute URL's
            images = re.findall('"page_image": ?"([^"]+)"', self.body)
            for image in images:
                self.body = self.body.replace(image, self.get_wiki_image(image), 1)
            # Converting and make sure this method acts functional
            content_type, data = super(WikipediaImagesMixin, self).content
            self.body = original_body
            self._json_body = data
        return "application/json", self._json_body

    @staticmethod
    def get_wiki_image(file_name):
        md5 = hashlib.md5(file_name.encode("utf-8"))
        hexhash = md5.hexdigest()
        return 'http://upload.wikimedia.org/wikipedia/commons/{}/{}/{}'.format(
            hexhash[:1],
            hexhash[:2],
            file_name
        )

    def __init__(self):
        super(WikipediaImagesMixin, self).__init__()
        self._json_body = None
