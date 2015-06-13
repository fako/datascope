from __future__ import unicode_literals, absolute_import, print_function, division
import six

import jsonschema
from jsonschema.exceptions import ValidationError as SchemaValidationError

from django.db import models
from django.core.exceptions import ValidationError

import jsonfield

from core.models.organisms import Organism
from core.utils.data import reach


class Individual(Organism):

    collective = models.ForeignKey('Collective', null=True)
    properties = jsonfield.JSONField(default={})

    def __getitem__(self, item):
        return self.properties[item]

    @staticmethod
    def validate(data, schema):
        """
        Validates the data against given schema and checks validity of ds_id and ds_spirit.

        :param data: The data to validate
        :param schema: The JSON schema to use for validation.
        :return: Valid data
        """
        if not isinstance(data, dict):
            raise ValidationError(
                "An Individual can only work with a dict as data and got {} instead".format(type(data))
            )
        pk = data.pop("ds_id", None)

        try:
            jsonschema.validate(data, schema)
        except SchemaValidationError as exc:
            raise ValidationError(exc)

        if pk and not isinstance(pk, six.integer_types):
            raise ValidationError("The id of an individual needs to be an integer not {}.".format(type(spirit)))
        elif pk:
            data["ds_id"] = pk

        return data

    def update(self, data, validate=True):
        """
        Update the properties and spirit with new data.

        :param data: The data to use for the update
        :param validate: (optional) whether to validate data or not (yes by default)
        :return: Updated content
        """
        if isinstance(data, (list, tuple,)):
            data = data[0]

        if validate:
            self.validate(data, self.schema)

        self.properties.update(data)
        self.save()
        return self.content

    @property
    def content(self):
        """
        Returns the content of this Individual

        :return: Dictionary filled with properties.
        """
        meta = {
            "ds_id": self.id,
        }
        return dict(
            {key: value for key, value in six.iteritems(self.properties) if not key.startswith('_')},
            **meta
        )

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

