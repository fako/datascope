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

    def get_entity(self, snak):
        """
        Turns Wikidata into a more readable entity data structure

        :param (dict) snak: a Wikidata specific data structure: https://www.mediawiki.org/wiki/Wikibase/DataModel#Snaks
        :return: A tuple with the format (entity, is_item).
        """
        print(snak)
        assert "property" in snak and "datavalue" in snak and "datatype" in snak, \
            "Wikidata snacs should have a property, datavalue and datatype specified"
        value = snak["datavalue"]["value"]
        if snak["datatype"] == "wikibase-item":

            return {
                "property": snak["property"],
                "value": "Q{}".format(value["numeric-id"]),
                "type": value["entity-type"]
            }, True
        else:
            return {
                "property": snak["property"],
                "value": value,
                "type": snak["datatype"]
            }, False

    @property
    def content(self):
        content_type, data = super(WikiDataClaims, self).content
        item = data["entities"][self.meta]
        raw_claims = []
        for raw_claims_list in item["claims"].values():
            raw_claims += raw_claims_list
        claim_entities = []
        references = set()
        for raw_claim in raw_claims:
            claim_entity, is_item = self.get_entity(raw_claim["mainsnak"])
            claim_entity["references"] = []
            for references_data in raw_claim.get("references", []):
                # We filter out the first item as the reference for all raw_references
                # This discards reference dates and reference URL data from the reference
                raw_references = []
                for raw_references_list in references_data["snaks"].values():
                    raw_references += raw_references_list
                raw_reference_entities = map(self.get_entity, raw_references)
                reference_entity = next(ref for ref, is_item in raw_reference_entities if is_item)
                reference = "{}:{}".format(reference_entity["property"], reference_entity["value"])
                claim_entity["references"].append(reference)
                references.add(reference)
            claim_entities.append(claim_entity)
        item["claims"] = claim_entities
        item["references"] = list(references)
        del item["labels"]
        del item["descriptions"]
        del item["aliases"]
        del item["sitelinks"]
        return content_type, item

    @property
    def meta(self):
        return self.request['args'][0]

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
