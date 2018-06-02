import subprocess
import string
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
    CMD_TEMPLATE = ["python", "manage.py", "shell", "CMD_FLAGS"]
    FLAGS = {
        "settings": "--settings="
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

    @property
    def content(self):
        return "application/json", self.transform(self.stdout)

    def variables(self, *args):
        raise NotImplementedError("Variables are not specified on this resource")

    def validate_command(self, command):
        pass

    def transform(self, stdout):
        return stdout

    def _create_command(self, *args, **kwargs):
        self._validate_input(*args, **kwargs)

        # First we format the command template
        formatter = string.Formatter()
        arguments = iter(args)
        cmd = []
        for part in self.CMD_TEMPLATE:
            fields = formatter.parse(part)
            for literal_text, field_name, format_spec, conversion in fields:
                if field_name is not None:
                    part = part.format(next(arguments))
            cmd.append(part)

        # Then we set the flags
        flags_index = cmd.index("CMD_FLAGS")
        flags = ""
        for key, value in kwargs.items():
            if key in self.FLAGS:
                flags += " " + self.FLAGS[key] + value
        flags = flags.lstrip()
        cmd[flags_index] = flags

        return {
            "args": args,
            "kwargs": kwargs,
            "cmd": cmd
        }

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
