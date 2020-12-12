from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _


class TimestampMixin(models.Model):

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("modified at"), auto_now=True)

    class Meta:
        abstract = True


class SiteMixin(models.Model):

    site = models.ForeignKey(Site, verbose_name=_("website"), on_delete=models.PROTECT)

    class Meta:
        abstract = True
