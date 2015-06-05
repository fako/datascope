from __future__ import unicode_literals, absolute_import, print_function, division

from core.models.organisms import Organism, Individual


class Collective(Organism):

    @staticmethod
    def validate(data, schema):
        """
        Validates the data against given schema for one of more Individuals.

        :param data: The data to validate
        :param schema: The JSON schema to use for validation.
        :return: Valid data
        """
        if not isinstance(data, list):
            data = [data]
        return [Individual.validate(instance, schema) for instance in data]

    def update(self, data, validate=True):
        """
        Update the instance with new data by adding to the Collective
        or by updating Individuals that are on the Collective.

        :param data: The data to use for the update
        :param validate: (optional) whether to validate data or not (yes by default)
        :return: A list of updated or created instances.
        """
        if validate:
            data = Collective.validate(data, self.schema)
        assert isinstance(data, (list, dict,)), \
            "Collective.update expects data to be formatted as list or dict not {}".format(type(data))

        updates = []
        if isinstance(data, dict):
            pk = data.pop("ds_id", None)
            if pk is None:
                individual = self.individual_set.create(
                    community=self.community,
                    schema=self.schema,
                    properties=data
                )
            else:
                individual = Individual.objects.get(pk=pk)
                individual.update(data)
                individual.collective = self
                individual.save()
            updates.append(individual)
        elif isinstance(data, list):
            for instance in data:
                updates += self.update(instance, validate=False)
        return updates

    @property
    def content(self):
        """
        Returns the content of the members of this Collective

        :return: a list of properties from Individual members
        """
        return [ind.content for ind in self.individual_set.all()]

    def group_by_collectives(self, key=None):
        """
        Outputs a dict with Collectives. The Collectives are filled with Individuals that hold the same value for key.

        :param key:
        :return:
        """
        pass
