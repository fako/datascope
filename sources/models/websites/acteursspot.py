from __future__ import unicode_literals, absolute_import, print_function, division

from core.models.resources.http import HttpResource
from core.exceptions import DSHttpError40X


class ActeursSpotProfile(HttpResource):

    URI_TEMPLATE = "https://www.acteursspot.nl/acteurprofiel.php?id={}"
    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "integer",
                    "maximum": 1700
                }
            ],
            "additionalItems": False,
        },
        "kwargs": None
    }
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
    }

    CONFIG_NAMESPACE = "acteurs_spot"

    def _handle_errors(self):
        super(ActeursSpotProfile, self)._handle_errors()
        if b"De acteur werd niet gevonden" in self.body or b"Dit profiel is nog niet zichtbaar" in self.body:
            self.status = 404
            raise DSHttpError40X("Not found", resource=self)