from django.db import models

import jsonfield

from core.models.storage import Storage


class ServiceStorage(Storage):

    completed_at = models.DateTimeField()
    views = models.IntegerField()
    content = jsonfield.JSONField(default=None)

    def save(self, *args, **kwargs):
        super(ServiceStorage, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class VisualTranslationsStorage(ServiceStorage):
    class Meta:
        app_label = "core"


class PeopleSuggestionsStorage(ServiceStorage):
    pass