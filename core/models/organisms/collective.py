from .organism import Organism


class Collective(Organism):

    @classmethod  # TODO: write manager instead!
    def create_from_list(cls, lst, schema, context=None):
        """
        Create new instance of this class from list if any dictionary inside validates against the schema.
        The matching dictionaries will be stored as Individual. If the context parameter is set to a dictionary.
        The Individuals get updated with the given dictionary.

        :param lst:
        :param schema:
        :param context: (optional)
        :return:
        """
        pass

    def add_from_list(self, lst, context=None):
        """
        Adds any dictionaries in list as Individual to this class if they validate against set schema.
        If the context parameter is set to a dictionary. The Individuals get updated with the given dictionary.

        :param lst:
        :param context: (optional)
        :return:
        """
        pass

    def list_json_path(self, json_path):
        """
        Returns a list consisting of values at json_path on Individuals that are members of this Collective.

        :param json_path:
        :return:
        """
        pass

    @property
    def content(self):
        """
        Returns the content of the members of this Collective

        :return: a list of properties from Individual members
        """
        return [ind.content for ind in self.individual_set.all()]  # TODO: fix QuerySet caching