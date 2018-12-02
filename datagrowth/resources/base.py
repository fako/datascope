import logging

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from datagrowth import configuration


log = logging.getLogger("datascope")


class Resource(models.Model):

    # Identification
    uri = models.CharField(max_length=255, db_index=True, default=None)
    status = models.PositiveIntegerField(default=0)

    # Configuration
    config = configuration.ConfigurationField(
        config_defaults=configuration.DEFAULT_CONFIGURATION,
    )

    # Archiving fields
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    purge_at = models.DateTimeField(null=True, blank=True)

    # Retention
    retainer = GenericForeignKey(ct_field="retainer_type", fk_field="retainer_id")
    retainer_type = models.ForeignKey(ContentType, null=True, blank=True)
    retainer_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True
        get_latest_by = "created_at"

    def retain(self, retainer):
        self.retainer = retainer
        self.save()

    @property
    def content(self):
        raise NotImplementedError("Missing implementation for content property on {}".format(self.__class__.__name__))
