from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

import json_field


class Organism(models.Model):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+")
    community_id = models.PositiveIntegerField()

    schema = json_field.JSONField(default=None, null=False, blank=False)  # BUG: schema does not throw IntegrityError on None

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def validate(data, schema):
        raise NotImplementedError()

    def update(self, data, validate=True):
        raise NotImplementedError()

    @property
    def content(self):
        raise NotImplementedError()

    def output(self, *args):
        raise NotImplementedError()

    @property
    def url(self):
        raise NotImplementedError()

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.id)

    class Meta:
        abstract = True
        get_latest_by = "created_at"
        ordering = ["created_at"]
