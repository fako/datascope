from __future__ import unicode_literals, absolute_import, print_function, division

from .organism import Organism


class Collective(Organism):

    def update(self, data):
        """
        Update the instance with new data. This property is meant to be overridden by subclasses.

        :param data:
        :return: None
        """
        return None

    @property
    def content(self):
        """
        Returns the content of the members of this Collective

        :return: a list of properties from Individual members
        """
        return [ind.content for ind in self.individual_set.all()]  # TODO: fix QuerySet caching

    def group_by_collectives(self, key=None):
        """
        Outputs a dict with Collectives. The Collectives are filled with Individuals that hold the same value for key.

        :param key:
        :return:
        """
        pass

    def group_by_spirit(self):
        """
        Groups individuals by their spirit

        :return:
        """
        pass
