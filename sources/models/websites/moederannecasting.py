from core.models.resources.http import HttpResource


class MoederAnneCastingSearch(HttpResource):
    URI_TEMPLATE = "http://zoekbestand.moederannecasting.nl/atlantispubliek/Resultaten.aspx"
    GET_SCHEMA = {
        "args": None,
        "kwargs": {
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "maximum": 620
                }
            }
        }
    }