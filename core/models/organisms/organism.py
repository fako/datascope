from django.db import models

from jsonfield import JSONField



class Organism(models.Model):
    community = models.ForeignKey('Community')
    schema = JSONField()
    spirit = models.CharField(max_length=255, db_index=True)  # should be unique per community?

    @classmethod  # TODO: write manager instead!
    def create_from_json(cls, json_string, schema, context=None):
        """
        Parses the json string into a data structure
        and then adds dictionaries inside a newly created Collective if any validates against the schema.
        The matching dictionaries will be stored as Individual. If the context parameter is set to a dictionary.
        The Individuals get updated with the given dictionary.

        :param json_string:
        :param schema:
        :param context:
        :return:
        """
        pass

    @classmethod  # TODO: write manager instead!
    def create_from_growth(cls, growth):
        """

        :param growth:
        :return:
        """
        pass

    def add_from_growth(self, growth):
        """

        :param growth:
        :return:
        """
        pass

    def add_from_json(self, json_string, schema, context=None):
        """
        Parses the json string into a data structure and then adds dictionaries to self if any validates against the schema.
        The matching dictionaries will be stored as Individual. If the context parameter is set to a dictionary.
        The Individuals get updated with the given dictionary.

        :param json_string:
        :param schema:
        :param context:
        :return:
        """
        pass

    @property
    def url(self, json_path=None):
        """
        TODO: Uses Django reverse
        Sets an anchor if json_path is given

        :param json_path: (optional)
        :return:
        """
        if not self.id:
            raise ValueError("Can't get path for unsaved Collective")
        return "ind|col/{}/".format(self.id)

    @property
    def content(self):
        """
        Return the content of the instance. This property is meant to be overridden by subclasses.

        :return: None
        """
        return None

    class Meta:
        abstract = True
        unique_together = ('community_id', 'spirit')