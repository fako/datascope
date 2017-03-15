from datetime import datetime
import logging

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from celery.result import AsyncResult
from json_field import JSONField

from core.models.resources.resource import Resource
from core.tasks import manifest_community
from core.exceptions import DSProcessUnfinished


log = logging.getLogger("datascope")


class Manifestation(Resource):

    data = JSONField(null=True)

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+")
    community_id = models.PositiveIntegerField()

    task = models.CharField(max_length=255, null=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def generate_config(allowed_config, **kwargs):
        config = {key: value for key, value in kwargs.items() if key in allowed_config}
        return config

    def get_data(self, async=False):
        if self.data:
            return self.data
        if self.task:
            result = AsyncResult(self.task)
            if not result.ready():
                raise DSProcessUnfinished("Manifest processing is not done")
            self.data = result.result
        if async:
            self.task = manifest_community.delay(self.id)
            self.save()
            raise DSProcessUnfinished("Manifest started processing")
        else:
            self.data = manifest_community(self.id)
        self.completed_at = datetime.now()
        self.save()
        return self.data

    def __str__(self):
        return "Manifestation {} for {}".format(
            self.id,
            self.community
        )

    @property
    def content(self):
        return "application/json", {
            "service": self.uri,
            "data": self.get_data()
        }
