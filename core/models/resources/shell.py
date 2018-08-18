import subprocess
import string
from copy import deepcopy
import jsonschema
from jsonschema.exceptions import ValidationError as SchemaValidationError

from django.db import models
from django.core.exceptions import ValidationError
import json_field

from core.models.resources.resource import Resource


class ShellResource(Resource):

    # Getting data
    command = json_field.JSONField(default=None)

    # Storing data
    stdout = models.TextField(default=None, null=True, blank=True)
    stderr = models.TextField(default=None, null=True, blank=True)

    # Class constants that determine behavior
    CMD_TEMPLATE = ["python", "manage.py", "shell"]
    FLAGS = {
        "settings": "--settings"
    }

    SCHEMA = {
        "arguments": {},
        "flags": {}
    }

    def run(self, *args, **kwargs):

        # create command from args, kwargs and command template
        # validate command
        # set URI
        # retrieve from cache resource=
        # _run
        # _handle_errors
        # return resource

        pass

    def validate_command(self, command):
        pass

    def transform(self):
        pass

    def line_to_dict(self, line):
        pass

    def _create_command(self, *args, **kwargs):
        self._validate_input(*args, **kwargs)

        # First we format the command template
        formatter = string.Formatter()
        arguments = iter(args)
        command = []
        for part in self.CMD_TEMPLATE:
            fields = formatter.parse(part)
            for literal_text, field_name, format_spec, conversion in fields:
                if field_name is not None:
                    part = part.format(next(arguments))
            command.append(part)

        # Then we set the flags
        flags_index = command.index("CMD_FLAGS")

        return command

    def _validate_input(self, *args, **kwargs):
        args_schema = self.SCHEMA.get("arguments")
        kwargs_schema = self.SCHEMA.get("flags")
        if args_schema is None and len(args):
            raise ValidationError("Received arguments for command where there should be none.")
        if kwargs_schema is None and len(kwargs):
            raise ValidationError("Received keyword arguments for command where there should be none.")
        if args_schema:
            try:
                jsonschema.validate(list(args), args_schema)
            except SchemaValidationError as ex:
                raise ValidationError(
                    "{}: {}".format(self.__class__.__name__, str(ex))
                )
        if kwargs_schema:
            try:
                jsonschema.validate(kwargs, kwargs_schema)
            except SchemaValidationError as ex:
                raise ValidationError(
                    "{}: {}".format(self.__class__.__name__, str(ex))
                )

    def _run(self):
        pass

    def _handle_errors(self):
        pass

    class Meta:
        abstract = True
