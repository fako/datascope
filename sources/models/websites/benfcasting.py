from __future__ import unicode_literals, absolute_import, print_function, division

from core.models.resources.http import HttpResource
from core.exceptions import DSHttpError40X


class BenfCastingProfile(HttpResource):

    URI_TEMPLATE = "http://www.benfcasting.nl/mods/models/index.php?p=viewModel&i={}"
    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "integer",
                    "maximum": 19000
                }
            ],
            "additionalItems": False,
        },
        "kwargs": None
    }
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
    }

    CONFIG_NAMESPACE = "benf_casting"

    def _handle_errors(self):
        super(BenfCastingProfile, self)._handle_errors()
        if not b"detailCell" in self.body:
            self.status = 404
            raise DSHttpError40X("Not found")

    def save(self, *args, **kwargs):
        self.body = "\n".join(self.body.split("\n")[1:])  # strip </body></html> from response :S
        super(BenfCastingProfile, self).save(*args, **kwargs)

    @property
    def query(self):
        return self.request["args"][0]
