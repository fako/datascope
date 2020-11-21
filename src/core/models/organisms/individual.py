from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType
from django.urls import reverse


from datagrowth.datatypes import DocumentBase, DocumentMysql


class Individual(DocumentMysql, DocumentBase):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+", on_delete=models.PROTECT)
    community_id = models.PositiveIntegerField()

    collective = models.ForeignKey('core.Collective', null=True, on_delete=models.CASCADE)

    @property
    def collection(self):
        return self.collective

    @property
    def url(self):
        if not self.id:
            raise ValueError("Can't get url for unsaved Individual")
        return reverse("v1:individual-content", args=[self.id])  # TODO: make version aware
