from __future__ import unicode_literals, absolute_import, print_function, division

from django.db import models

from datascope.configuration import DEFAULT_CONFIGURATION
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from core.utils import configuration


class ShellResource(models.Model):

    uri = models.CharField(max_length=255, db_index=True, default=None)
    # Configuration
    config = configuration.ConfigurationField(
        config_defaults=DEFAULT_CONFIGURATION,
    )
    # Archiving fields
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    purge_at = models.DateTimeField(null=True, blank=True)

    # Retention
    retainer = GenericForeignKey(ct_field="retainer_type", fk_field="retainer_id")
    retainer_type = models.ForeignKey(ContentType, null=True)
    retainer_id = models.PositiveIntegerField(null=True)

    def execute(self):
        pass
