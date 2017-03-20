from urlobject import URLObject

from core.models.resources.http import HttpResource, URLResource


class OfficialAnnouncementsNetherlands(HttpResource):

    URI_TEMPLATE = "https://zoek.officielebekendmakingen.nl/zoeken/resultaat/?spd={}&epd={}"

    DATE_FORMAT = "%Y%m%d"

    PARAMETERS = {
        "zkt": "Uitgebreid",
        "pst": "ParlementaireDocumenten",
        "dpr": "AnderePeriode",
        "kmr": "TweedeKamerderStatenGeneraal",
        "sdt": "KenmerkendeDatum",
        "par": "Handeling",
        "dst": "Onopgemaakt|Opgemaakt|Opgemaakt+na+onopgemaakt",
        "isp": "true",
        "pnr": 1,
        "rpp": 10,
        "sorttype": 1,
        "sortorder": 4
    }

    CONFIG_NAMESPACE = "dutch_government"

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
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

    def __init__(self, *args, **kwargs):
        super(OfficialAnnouncementsNetherlands, self).__init__(*args, **kwargs)
        self.page = 1

    def next_parameters(self):
        content_type, data = self.content
        next_link = data.find("a", class_="volgende")
        if next_link is None:
            return None
        next_url = URLObject(next_link.get("href"))
        return {
            "_page": next_url.query_dict["_page"]
        }

    class Meta:
        verbose_name = "Official announcements (Dutch)"
        verbose_name_plural = "Official announcements (Dutch)"


class OfficialAnnouncementsDocumentNetherlands(URLResource):

    class Meta:
        verbose_name = "Official announcements document (Dutch)"
        verbose_name_plural = "Official announcements document (Dutch)"
