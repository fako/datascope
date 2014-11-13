from datetime import datetime, timedelta

from django.db import models

from rest_framework.status import HTTP_200_OK
import jsonfield

from core.models.storage import Storage


class ServiceStorage(Storage):

    completed_at = models.DateTimeField(null=True, blank=True)
    views = models.IntegerField(default=1)
    content = jsonfield.JSONField(default=None)

    HIF_success_statusses = [HTTP_200_OK]

    def save(self, *args, **kwargs):
        self.purge_at = datetime.now() + timedelta(days=3)
        if self.status in self.HIF_success_statusses:
            self.completed_at = datetime.now()
        super(ServiceStorage, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class VisualTranslationsStorage(ServiceStorage):
    class Meta:
        app_label = "core"  # TODO: change when migrating to 1.7
        db_table = "core_visualtranslations"
        verbose_name = "Visual Translations"
        verbose_name_plural = "Visual Translations"


class PeopleSuggestionsStorage(ServiceStorage):
    class Meta:
        app_label = "core"  # TODO: change when migrating to 1.7
        db_table = "core_peoplesuggestions"
        verbose_name = "People Suggestions"
        verbose_name_plural = "People Suggestions"


class CityCelebritiesStorage(ServiceStorage):
    class Meta:
        app_label = "core"  # TODO: change when migrating to 1.7
        db_table = "core_citycelebrities"
        verbose_name = "City Celebrities"
        verbose_name_plural = "City Celebrities"