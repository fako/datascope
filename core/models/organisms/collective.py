from django.apps import apps
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType
from django.core.urlresolvers import reverse

from datagrowth.datatypes import Collection


class Collective(Collection):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+")
    community_id = models.PositiveIntegerField()

    @classmethod
    def get_document_model(cls):
        return apps.get_model("core.Individual")

    @property
    def documents(self):
        return self.individual_set

    def create_document(self, data):
        Individual = self.get_document_model()
        return Individual(
            community=self.community,
            collective=self,
            schema=self.schema,
            properties=data
        )

    def update(self, data, validate=True, reset=True, batch_size=500):
        return self.add(data, validate=validate, reset=reset, batch_size=batch_size)

    @property
    def url(self):
        if not self.id:
            raise ValueError("Can't get url for unsaved Collective")
        return reverse("v1:collective-content", args=[self.id])  # TODO: make version aware
