from __future__ import unicode_literals, absolute_import, print_function, division
import six

from core.utils.helpers import override_dict
from sources.models.wikipedia.base import WikipediaAPI


class WikiDataItems(WikipediaAPI):

    URI_TEMPLATE = "https://www.wikidata.org/w/api.php?ids={}"

    PARAMETERS = override_dict(WikipediaAPI.PARAMETERS, {
        "action": "wbgetentities",
        "languages": "en",
        "redirects": "yes",
        "props": "info|claims|descriptions"
    })

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [{"type": "string"}],  # TODO: use a pattern?
        },
        "kwargs": None
    }

    class Meta:
        verbose_name = "Wikidata items"
        verbose_name_plural = "Wikidata items"

    def get_entity(self, snak):
        """
        Turns Wikidata into a more readable entity data structure

        :param (dict) snak: a Wikidata specific data structure: https://www.mediawiki.org/wiki/Wikibase/DataModel#Snaks
        :return: A tuple with the format (entity, is_item).
        """
        assert "property" in snak and "datatype" in snak and "snaktype" in snak, \
            "Wikidata snacs should have a property and datatype specified"
        if snak["snaktype"] == "novalue" or snak["snaktype"] == "somevalue":
            return {
                "property": snak["property"],
                "type": snak["datatype"],
                "value": None
            }, snak["datatype"] == "wikibase-item"
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

    def get_item(self, raw_item_data):
        raw_claims = []
        for raw_claims_list in six.itervalues(raw_item_data["claims"]):
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
                try:
                    reference_entity = next(ref for ref, is_item in raw_reference_entities if is_item)
                except StopIteration:
                    continue
                reference = "{}:{}".format(reference_entity["property"], reference_entity["value"])
                claim_entity["references"].append(reference)
                references.add(reference)
            claim_entities.append(claim_entity)
        item = raw_item_data
        try:
            item["description"] = item["descriptions"]["en"]["value"]
        except KeyError:
            item["description"] = "No English description available"
        del item["descriptions"]
        item["claims"] = claim_entities
        item["references"] = list(references)
        return item

    def _handle_errors(self):
        content_type, data = super(WikiDataItems, self).content
        if data is not None and "error" in data:
            error_code = data["error"]["code"]
            self.set_error(self.ERROR_CODE_TO_STATUS[error_code])
        super(WikiDataItems, self)._handle_errors()

    @property
    def content(self):
        content_type, data = super(WikiDataItems, self).content
        items = []
        for raw_item in data.get("entities", {}).values():
            items.append(self.get_item(raw_item))
        return content_type, items
