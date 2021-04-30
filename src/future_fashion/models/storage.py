from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin, DocumentBase, DocumentPostgres


class Collection(DocumentCollectionMixin, CollectionBase):

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


class Document(DocumentPostgres, DocumentBase):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+", on_delete=models.PROTECT)
    community_id = models.PositiveIntegerField()
