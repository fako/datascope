from __future__ import unicode_literals, absolute_import, print_function, division
import six

import jsonschema
from jsonschema.exceptions import ValidationError as SchemaValidationError

from django.db import models
from django.core.exceptions import ValidationError

import json_field

from core.models.organisms import Organism
from core.utils.data import reach


class Individual(Organism):

    collective = models.ForeignKey('Collective', null=True)
    properties = json_field.JSONField(default={})

    identity = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    index = models.SmallIntegerField(blank=True, null=True)

    def __getitem__(self, key):
        return self.properties[key]

    def __setitem__(self, key, value):
        self.properties[key] = value

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

        try:
            jsonschema.validate(properties, schema)
        except SchemaValidationError as exc:
            raise ValidationError(exc)

    def update(self, data, validate=True):
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
            {key: value for key, value in six.iteritems(self.properties) if not key.startswith('_')},
        )

    @property
    def json_content(self):
        return self.get_properties_json()

    def output(self, *args):
        if len(args) > 1:
            return map(self.output, args)
        frm = args[0]
        if not frm:
            return frm
        if isinstance(frm, six.string_types):
            return reach(frm, self.properties)
        elif isinstance(frm, list):
            return self.output(*frm) if len(frm) > 1 else [self.output(*frm)]
        elif isinstance(frm, dict):
            return {key: self.output(value) for key, value in six.iteritems(frm)}
        else:
            raise AssertionError("Expected a string, list or dict as argument got {} instead".format(type(frm)))

    def items(self):
        return self.properties.items()

    def keys(self):
        return self.properties.keys()

    def values(self):
        return self.properties.values()

    def clean(self):
        if self.collective:
            self.collective.influence(self)
