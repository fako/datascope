from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType


class Collection(object):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+", on_delete=models.PROTECT)
    community_id = models.PositiveIntegerField()

    def init_document(self, data, collection=None):
        Document = self.get_document_model()
        return Document(
            community=self.community,
            collection=collection,
            properties=data
        )


class Document(object):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+", on_delete=models.PROTECT)
    community_id = models.PositiveIntegerField()
