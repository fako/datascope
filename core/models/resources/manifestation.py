from datetime import datetime
import logging

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from celery.result import AsyncResult
from json_field import JSONField

from core.models.resources.resource import Resource
from core.exceptions import DSProcessUnfinished


log = logging.getLogger("datascope")


class Manifestation(Resource):

    data = JSONField(null=True)

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+")
    community_id = models.PositiveIntegerField()

    task = models.CharField(max_length=255, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def generate_config(allowed_config, **kwargs):
        config = {key: value for key, value in kwargs.items() if key in allowed_config}
        return config

    def get_data(self, async=False):  # TODO: set celery states into the status field
        from core.tasks import get_manifestation_data
        if self.data:
            return self.data
        if self.task:
            result = AsyncResult(self.task)
            if not result.ready():
                raise DSProcessUnfinished("Manifest processing is not done")
            elif result.successful():
                self.data = result.result
            elif result.failed():
                self.data = str(result.result)
            else:
                raise AssertionError("get_data is not handling AsyncResult with status: {}".format(result.status))
        elif async:
            self.task = get_manifestation_data.delay(self.id)
            self.save()
            raise DSProcessUnfinished("Manifest started processing")
        else:
            self.data = get_manifestation_data(self.id)
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
