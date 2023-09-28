from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin, DocumentBase


class Collection(DocumentCollectionMixin, CollectionBase):

    dataset_version = None  # prevents having to declare a DatasetVersion model

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+", on_delete=models.PROTECT)
    community_id = models.PositiveIntegerField()

    def build_document(self, data, collection=None):
        Document = self.get_document_model()
        return Document(
            community=self.community,
            collection=collection,
            properties=data
        )


class Document(DocumentBase):

    dataset_version = None  # prevents having to declare a DatasetVersion model

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+", on_delete=models.PROTECT)
    community_id = models.PositiveIntegerField()

    def to_search(self):
        content = " ".join(partial for partial in self.properties["content"] if partial)
        return {
            "_id": self.id,
            "title": self.properties["title"],
            "title_plain": self.properties["title"],
            "argument_score": float(self.properties.get("argument_score", 0.0001)),
            "url": self.properties["url"],
            "author": self.properties["author"],
            "source": self.properties["source"],
            "content": content,
            "content_plain": content
        }
