from django.db import models


class AnnotationBase(models.Model):

    user = models.ForeignKey("User", blank=True, null=True)
    reference = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    value = models.FloatField(blank=True, null=True)
    string = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
