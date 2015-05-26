from django.db import models

import jsonfield

from .organism import Organism


class Individual(Organism):

    collective = models.ForeignKey('Collective', null=True)
    properties = jsonfield.JSONField()

    def __getattr__(self, item):
        return getattr(self.properties, item)

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
        Returns the content of this Individual

        :return: properties dictionary
        """
        return self.properties