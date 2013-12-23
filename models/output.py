from django.db import models

import jsonfield


class ServiceStorage(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField()
    completed_at = models.DateTimeField()
    purge_at = models.DateTimeField()

    identification = models.CharField(max_length=256)  # TODO: rename consistently to identity (and identify())
    views = models.IntegerField()
    content = jsonfield.JSONField()

    def save(self, *args, **kwargs):
        super(ServiceStorage, self).save(*args, **kwargs)

    class Meta:
        abstract = True

class ImageTranslationsStorage(ServiceStorage):
    pass

