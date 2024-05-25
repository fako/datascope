from django.apps import apps
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType
from django.urls import reverse

from datagrowth.datatypes import CollectionBase
from core.models.organisms.backward_compatability import SupressDatasetVersionFeatures


class Collective(SupressDatasetVersionFeatures, CollectionBase):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+", on_delete=models.PROTECT)
    community_id = models.PositiveIntegerField()

    @classmethod
    def get_document_model(cls):
        return apps.get_model("core.Individual")

    @property
    def documents(self):
        return self.individual_set

    def build_document(self, data, collection=None):
        Individual = self.get_document_model()
        return Individual(
            community=self.community,
            collective=self,
            properties=data
        )

    @property
    def url(self):
        if not self.id:
            raise ValueError("Can't get url for unsaved Collective")
        return reverse("v1:core:collective-content", args=[self.id])
