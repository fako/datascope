from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType
from django.core.urlresolvers import reverse

import json_field

from datagrowth.datatypes import DocumentBase, DocumentMysql


class Individual(DocumentBase, DocumentMysql):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+")
    community_id = models.PositiveIntegerField()

    collective = models.ForeignKey('core.Collective', null=True)

    @property
    def collection(self):
        return self.collective

    @property
    def url(self):
        if not self.id:
            raise ValueError("Can't get url for unsaved Individual")
        return reverse("v1:individual-content", args=[self.id])  # TODO: make version aware
