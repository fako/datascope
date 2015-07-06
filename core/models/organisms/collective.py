from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf import settings
from django.core.urlresolvers import reverse

from core.models.organisms import Organism, Individual


class Collective(Organism):

    @property
    def url(self):
        if not self.id:
            raise ValueError("Can't get url for unsaved Collective")
        return reverse("v1:collective-content", args=[self.id])  # TODO: make version aware

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
        Individual.objects.bulk_create(bulks, batch_size=settings.MAX_BATCH_SIZE)
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
            output = self.output(*frm)
            if len(frm) > 1:
                output = [list(zipped) for zipped in zip(*output)]
            else:
                output = [[out] for out in output]
            return output
        else:
            return [ind.output(frm) for ind in self.individual_set.all()]

    def group_by(self, key):
        """
        Outputs a dict with lists. The lists are filled with Individuals that hold the same value for key.

        :param key:
        :return:
        """
        grouped = {}
        for ind in self.individual_set.all():
            assert key in ind.properties, \
                "Can't group by {}, because it is missing from an individual on collective {}".format(key, self.id)
            value = ind.properties[key]
            if value not in grouped:
                grouped[value] = [ind]
            else:
                grouped[value].append(ind)
        return grouped
