import six

from django.db import models

import jsonfield

from .organism import Organism


class Individual(Organism):

    collective = models.ForeignKey('Collective', null=True)
    properties = jsonfield.JSONField()

    def __getitem__(self, item):
        return self.properties[item]

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
        meta = {
            "ds_id": self.id,
            "ds_spirit": self.spirit
        }
        return dict(
            {key: value for key, value in six.iteritems(self.properties) if not key.startswith('_')},
            **meta
        )
