from __future__ import unicode_literals, absolute_import, print_function, division
from django.utils.encoding import python_2_unicode_compatible

from django.db import models

from jsonfield import JSONField


@python_2_unicode_compatible
class Organism(models.Model):

    #community = models.ForeignKey('Community')
    schema = JSONField(default=None, null=False, blank=False)  # BUG: schema does not throw IntegrityError on None

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

    @property
    def url(self):
        """
        TODO: Uses Django reverse

        :return:
        """
        if not self.id:
            raise ValueError("Can't get path for unsaved Collective")
        return "ind|col/{}/".format(self.id)

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.id)

    class Meta:
        abstract = True
