from __future__ import unicode_literals, absolute_import, print_function, division

from core.models.resources.http import HttpResource


class WikiDataClaims(HttpResource):

    URI_TEMPLATE = "https://www.wikidata.org/wiki/Special:EntityData/{}.json"  # updated at runtime
    CONFIG_NAMESPACE = 'wikipedia'

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [{"type": "string"}],
        },
        "kwargs": None
    }

    HIF_objective = {
        "property": "",
        "datavalue.value.numeric-id": 0
    }
    HIF_translations = {
        "datavalue.value.numeric-id": "item"
    }

    # def cleaner(self, result_instance):
    #     return result_instance['item'] and result_instance['property'] not in self.config.excluded_properties
    #
    # @property
    # def rsl(self):
    #     claims = self.data
    #     unique_claims = {"{}:{}".format(claim['property'], claim['item']): claim for claim in claims}.values()
    #     return unique_claims
