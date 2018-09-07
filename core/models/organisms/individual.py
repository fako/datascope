from itertools import repeat

import jsonschema
from jsonschema.exceptions import ValidationError as SchemaValidationError

from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

import json_field

from core.models.organisms import Organism
from core.utils.data import reach


class Individual(Organism):

    collective = models.ForeignKey('core.Collective', null=True)
    properties = json_field.JSONField(default={})

    identity = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    index = models.SmallIntegerField(blank=True, null=True)

    def __getitem__(self, key):
        return self.properties[key]

    def __setitem__(self, key, value):
        self.properties[key] = value

    @property
    def url(self):
        if not self.id:
            raise ValueError("Can't get url for unsaved Individual")
        return reverse("v1:individual-content", args=[self.id])  # TODO: make version aware

    @staticmethod
    def validate(data, schema):
        """
        Validates the data against given schema and checks validity of ds_id and ds_spirit.

        :param data: The data to validate
        :param schema: The JSON schema to use for validation.
        :return: Valid data
        """

        if isinstance(data, dict):
            properties = data
        elif isinstance(data, Individual):
            properties = data.properties
        else:
            raise ValidationError(
                "An Individual can only work with a dict as data and got {} instead".format(type(data))
            )
        if "_id" in properties:
            del properties["_id"]

        try:
            jsonschema.validate(properties, schema)
        except SchemaValidationError as exc:
            django_exception = ValidationError(exc.message)
            django_exception.schema = exc.schema
            raise django_exception

    def update(self, data, validate=True):  # TODO: test to unlock
        """
        Update the properties and spirit with new data.

        :param data: The data to use for the update
        :param validate: (optional) whether to validate data or not (yes by default)
        :return: Updated content
        """
        if isinstance(data, (list, tuple,)):
            data = data[0]

        self.properties.update(data)

        if validate:
            self.validate(self.properties, self.schema)

        self.save()
        return self.content

    @property
    def content(self):
        """
        Returns the content of this Individual

        :return: Dictionary filled with properties.
        """
        return dict(
            {key: value for key, value in self.properties.items() if not key.startswith('_')},
            _id=self.id
        )

    @property
    def json_content(self):
        return self.get_properties_json()

    def output(self, *args):
        return self.output_from_content(self.properties, *args)

    @staticmethod
    def output_from_content(content, *args):  # TODO: test to unlock
        if len(args) > 1:
            return map(Individual.output_from_content, repeat(content), args)
        frm = args[0]
        if not frm:
            return frm
        if isinstance(frm, str):
            return reach(frm, content)
        elif isinstance(frm, list):
            if len(frm) > 1:
                return Individual.output_from_content(content, *frm)
            else:
                return [Individual.output_from_content(content, *frm)]
        elif isinstance(frm, dict):
            return {key: Individual.output_from_content(content, value) for key, value in frm.items()}
        else:
            raise AssertionError("Expected a string, list or dict as argument got {} instead".format(type(frm)))

    def items(self):
        return self.properties.items()

    def keys(self):
        return self.properties.keys()

    def values(self):
        return self.properties.values()

    def clean(self):
        # Always influence first!
        if self.collective:
            self.collective.influence(self)
        # After influence check integrity
        identity_max_length = Individual._meta.get_field('identity').max_length
        if self.identity and isinstance(self.identity, str) and len(self.identity) > identity_max_length:
            self.identity = self.identity[:identity_max_length]
