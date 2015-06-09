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

        def prepare_updates(data):

            bulk = []
            save = []
            if isinstance(data, dict):
                pk = data.pop("ds_id", None)
                if pk is None:
                    individual = Individual(
                        community=self.community,
                        collective=self,
                        schema=self.schema,
                        properties=data
                    )
                    bulk.append(individual)
                else:
                    individual = Individual.objects.get(pk=pk)
                    individual.update(data)
                    individual.collective = self
                    save.append(individual)
            else:  # type is list
                for instance in data:
                    extra_bulk, extra_save = prepare_updates(instance)
                    bulk += extra_bulk
                    save += extra_save
            return bulk, save

        bulks, saves = prepare_updates(data)
        Individual.objects.bulk_create(bulks)
        for organism in saves:
            organism.save()

    @property
    def content(self):
        """
        Returns the content of the members of this Collective

        :return: a list of properties from Individual members
        """
        return [ind.content for ind in self.individual_set.all()]

    def output(self, *args):
        if len(args) > 1:
            return map(self.output, args)
        frm = args[0]
        if not frm:
            return [frm for ind in self.individual_set.all()]
        elif isinstance(frm, list):
            return self.output(*frm)
        else:
            return [ind.output(frm) for ind in self.individual_set.all()]

    def group_by_collectives(self, key=None):
        """
        Outputs a dict with Collectives. The Collectives are filled with Individuals that hold the same value for key.

        :param key:
        :return:
        """
        pass
