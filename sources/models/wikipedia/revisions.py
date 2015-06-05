from __future__ import unicode_literals, absolute_import, print_function, division

import re
from copy import copy
import time
import math

from core.utils.helpers import override_dict
from core.exceptions import DSHttpWarning300

from sources.models.wikipedia.query import WikipediaQuery


class WikipediaRecentChanges(WikipediaQuery):

    URI_TEMPLATE = 'http://{}.wikipedia.org/w/api.php?rcstart={}&rcend={}'
    PARAMETERS = override_dict(WikipediaQuery.PARAMETERS, {
        "list": "recentchanges",
        "rcnamespace": 0,
        "rcshow": "!bot|!minor|!redirect",
        "rclimit": 500,
        "rcprop": "ids|title|comment|timestamp|tags",
        "rcdir": "newer"
    })
    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [{"type": "string"}, {"type": "integer"}],
            "minItems": 3,
            "maxItems": 3
        },
        "kwargs": None
    }

    CONFIG_NAMESPACE = "wikipedia"
    WIKI_RESULTS_KEY = "recentchanges"

    def send(self, method, *args, **kwargs):
        now = 1433495844 #int(time.time())
        past = now - (60 * 60 * 24)
        args = (self.config.wiki_country, past, now)
        return super(WikipediaQuery, self).send(method, *args, **kwargs)

