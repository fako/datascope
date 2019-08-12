from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from datagrowth.datatypes import CollectionBase, DocumentBase, DocumentPostgres


class Collection(CollectionBase):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+")
    community_id = models.PositiveIntegerField()

    def init_document(self, data, collection=None):
        Document = self.get_document_model()
        return Document(
            community=self.community,
            collection=collection,
            schema=self.schema,
            properties=data
        )


class Document(DocumentBase, DocumentPostgres):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+")
    community_id = models.PositiveIntegerField()
