from copy import copy
from urlobject import URLObject

from core.models.resources.http import HttpResource, URLResource


class DutchParlementRecordSearch(HttpResource):

    URI_TEMPLATE = "https://zoek.officielebekendmakingen.nl/resultaten"

    DATE_FORMAT = "%Y%m%d"
    SEARCH_FILTERS = [
        '(c.product-area=="officielepublicaties")',
        '((dt.creator=="Tweede Kamer der Staten-Generaal")or(dt.creator=="Tweede Kamer OCV / UCV"))',
        '(w.publicatienaam=="Handelingen")'
    ]

    PARAMETERS = {
        "pg": 10,
        "col": "AlleParlementaireDocumenten",
        "svel": "Kenmerkendedatum",
        "svol": "Aflopend",
        "sf": "ru|Handeling",
    }

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string"
                },
                {
                    "type": "string",
                    "format": "date-time"
                },
                {
                    "type": "string",
                    "format": "date-time"
                }
            ],
            "minItems": 2,
            "additionalItems": False
        },
        "kwargs": None
    }

    def variables(self, *args):
        return {
            "topic": args[0],
            "date_range": args[1:]
        }

    def parameters(self, topic, date_range, **kwargs):
        parameters = super().parameters()
        search_filters = copy(self.SEARCH_FILTERS)
        search_filters.append(f'(dt.subject="{topic}")')
        search_filters.append('(dt.date>="{}" and dt.date<="{}")'.format(*date_range))
        parameters["q"] = "and".join(search_filters)
        return parameters

    def next_parameters(self):
        content_type, data = self.content
        next_link = data.find("a", id="id-page-next")
        if next_link is None:
            return None
        next_url = URLObject(next_link.get("href"))
        return {
            "pagina": next_url.query_dict["pagina"]
        }


class DutchParlementRecord(URLResource):
    pass
