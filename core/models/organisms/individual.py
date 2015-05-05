from django.db import models

import jsonfield

from .organism import Organism


class Individual(Organism):

    collective = models.ForeignKey('Collective', null=True)
    properties = jsonfield.JSONField()

    def __getattr__(self, item):
        return getattr(self.properties, item)

    @classmethod  # TODO: write manager instead!
    def create_from_dict(cls, dic, schema):
        """
        Create new instance of this class from a dictionary if it validates against the schema.

        :param dic:
        :param schema:the schema to validate against
        :return:
        """
        pass

    def update_from_dict(self, dic):
        """
        Override existing properties with values from dic if it validates against the schema.

        :param dic:
        :return:
        """
        pass

    @property
    def content(self):
        """
        Returns the content of this Individual

        :return: properties dictionary
        """
        return self.properties