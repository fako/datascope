import json
from collections import Iterator, Iterable

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder

import json_field

from core.models.organisms import Organism, Individual
from core.utils.helpers import ibatch
from core.utils.data import reach


class Collective(Organism):  # TODO: rename to family

    identifier = models.CharField(max_length=255, null=True, blank=True)

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
        if not isinstance(data, Iterable):
            data = [data]
        for instance in data:
            Individual.validate(instance, schema)

    def update(self, data, validate=True, reset=True, batch_size=500):  # TODO: rename to "add" and implement "update"
        """
        Update the instance with new data by adding to the Collective
        or by updating Individuals that are on the Collective.

        :param data: The data to use for the update
        :param validate: (optional) whether to validate data or not (yes by default)
        :return: A list of updated or created instances.
        """
        assert isinstance(data, (Iterator, list, tuple, dict, Individual)), \
            "Collective.update expects data to be formatted as iteratable, dict or Individual not {}".format(type(data))

        if reset:
            self.individual_set.all().delete()

        def prepare_updates(data):

            prepared = []
            if isinstance(data, dict):
                if validate:
                    Individual.validate(data, self.schema)
                individual = Individual(
                    community=self.community,
                    collective=self,
                    schema=self.schema,
                    properties=data
                )
                individual.clean()
                prepared.append(individual)
            elif isinstance(data, Individual):
                if validate:
                    Individual.validate(data, self.schema)
                data.id = None
                data.collective = self
                data.clean()
                prepared.append(data)
            else:  # type is list
                for instance in data:
                    prepared += prepare_updates(instance)
            return prepared

        update_count = 0
        for updates in ibatch(data, batch_size=batch_size):
            updates = prepare_updates(updates)
            update_count += len(updates)
            Individual.objects.bulk_create(updates, batch_size=settings.MAX_BATCH_SIZE)

        return update_count

    @property
    def content(self):
        """
        Returns the content of the members of this Collective

        :return: a generator yielding properties from Individual members
        """
        return (ind.content for ind in self.individual_set.iterator())

    @property
    def has_content(self):
        """
        Indicates if Collective entails Individuals or not

        :return: True if there are Individuals, False otherwise
        """
        return self.individual_set.exists()

    @property
    def json_content(self):
        json_content = [ind.json_content for ind in self.individual_set.all()]
        return "[{}]".format(",".join(json_content))

    def split(self, train=0.8, validate=0.1, test=0.1, query_set=None, as_content=False):  # TODO: test to unlock
        assert train + validate + test == 1.0, "Expected sum of train, validate and test to be 1"
        assert train > 0, "Expected train set to be bigger than 0"
        assert validate > 0, "Expected validate set to be bigger than 0"
        query_set = query_set or self.individual_set
        content_count = query_set.count()
        # TODO: take into account that random ordering in MySQL is a bad idea
        # Details: http://www.titov.net/2005/09/21/do-not-use-order-by-rand-or-how-to-get-random-rows-from-table/
        individuals = query_set.order_by("?").iterator()
        test_set = []
        if test:
            test_size = round(content_count * test)
            test_set = [next(individuals) for ix in range(0, test_size)]
        validate_size = round(content_count * validate)
        validate_set = [next(individuals) for ix in range(0, validate_size)]
        return (
            (individual.content if as_content else individual for individual in individuals),
            [individual.content if as_content else individual for individual in validate_set],
            [individual.content if as_content else individual for individual in test_set]
        )

    def output(self, *args):
        if len(args) > 1:
            return map(self.output, args)
        frm = args[0]
        if not frm:
            return [frm for ind in range(0, self.individual_set.count())]
        elif isinstance(frm, list):
            output = self.output(*frm)
            if len(frm) > 1:
                output = [list(zipped) for zipped in zip(*output)]
            else:
                output = [[out] for out in output]
            return output
        else:
            return [ind.output(frm) for ind in self.individual_set.iterator()]

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

    def influence(self, individual):
        """
        This allows the Collective to set some attributes and or properties on the Individual

        :param individual: The individual that should be influenced
        :return: The influenced individual
        """
        if self.identifier:
            individual.identity = reach("$." + self.identifier, individual.properties)
        return individual

    def to_file(self, file_path):
        with open(file_path, "w") as json_file:
            json.dump(list(self.content), json_file, cls=DjangoJSONEncoder)
