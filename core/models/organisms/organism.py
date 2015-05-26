from django.db import models

from jsonfield import JSONField


class Organism(models.Model):

    community = models.ForeignKey('Community')
    schema = JSONField()
    spirit = models.CharField(max_length=255, db_index=True)

    def update(self, data):
        """
        Update the instance with new data. This property is meant to be overridden by subclasses.

        :return: None

        :param data:
        :return:
        """

    @property
    def content(self):
        """
        Return the content of the instance. This property is meant to be overridden by subclasses.

        :return: None
        """
        return None

    @property
    def url(self):
        """
        TODO: Uses Django reverse

        :return:
        """
        if not self.id:
            raise ValueError("Can't get path for unsaved Collective")
        return "ind|col/{}/".format(self.id)

    class Meta:
        abstract = True
