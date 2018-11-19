import subprocess
import string
import jsonschema
from copy import copy
from datetime import datetime
from jsonschema.exceptions import ValidationError as SchemaValidationError

from django.db import models
from django.core.exceptions import ValidationError
import json_field

from datagrowth import settings as datagrowth_settings
from datagrowth.resources.base import Resource
from datagrowth.exceptions import DGShellError


class ShellResource(Resource):
    # TODO: make sphinx friendly and doc all methods
    """
    A representation to store data from shell sources.
    The resource stores the stdin, stdout and stderr from commands.
    It acts as a wrapper around the subprocess module and provides:
     - output from database when commands ran before
     - possibility to hook command output into pipelines with other resources
    """

    # Getting data
    command = json_field.JSONField(default=None)
    stdin = models.TextField(default=None, null=True, blank=True)

    # Storing data
    stdout = models.TextField(default=None, null=True, blank=True)
    stderr = models.TextField(default=None, null=True, blank=True)

    # Class constants that determine behavior
    CMD_TEMPLATE = ["python", "manage.py", "shell", "CMD_FLAGS"]
    FLAGS = {
        "settings": "--settings="
    }
    VARIABLES = {}
    DIRECTORY_SETTING = None
    CONTENT_TYPE = "text/plain"

    SCHEMA = {
        "arguments": {},
        "flags": {}
    }

    #######################################################
    # PUBLIC FUNCTIONALITY
    #######################################################
    # Call run to execute the command
    # Success and content are to handle the results
    # Override transform to manipulate command results

    def run(self, *args, **kwargs):
        """
        Executes the command

        :param args: gets passed on to the command as positional arguments
        :param kwargs: gets passed on to the command as flags
        :return: self
        """

        if not self.command:
            self.command = self._create_command(*args, **kwargs)
            self.uri = self.uri_from_cmd(self.command.get("cmd"))
        else:
            self.validate_command(self.command)

        self.clean()  # sets self.uri
        resource = None
        try:
            resource = self.__class__.objects.get(
                uri=self.uri,
                stdin=self.stdin
            )
            self.validate_command(resource.command)
        except (self.DoesNotExist, ValidationError):
            if resource is not None:
                resource.delete()
            resource = self

        if resource.success:
            return resource

        resource._run()
        resource._handle_errors()
        return resource

    @property
    def success(self):
        """
        Returns True if exit code is within success range
        """
        return self.status == 0 and self.stdout

    @property
    def content(self):
        return self.CONTENT_TYPE, self.transform(self.stdout)

    def transform(self, stdout):
        """
        Override this method for particular commands.
        It takes the stdout from the command and transforms it into useful output for other components.
        One use case could be to clean out log lines from the output.

        :param stdout: the stdout from the command
        :return: transformed stdout
        """
        return stdout

    def environment(self, *args, **kwargs):
        if not self.VARIABLES:
            return None
        else:
            return self.VARIABLES

    def debug(self):
        print(subprocess.list2cmdline(self.command.get("cmd", [])))

    #######################################################
    # CREATE COMMAND
    #######################################################
    # A set of methods to create a command dictionary
    # The values inside are passed to the subprocess library

    def variables(self, *args):
        args = args or self.command.get("args")
        return {
            "input": args
        }

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
        flags = ""
        try:
            flags_index = cmd.index("CMD_FLAGS")
        except ValueError:
            flags_index = None
        if flags_index is not None:
            for key, value in kwargs.items():
                if key in self.FLAGS:
                    flags += " " + self.FLAGS[key] + value
            flags = flags.lstrip()
            cmd[flags_index] = flags

        # Returning command
        command = {
            "args": args,
            "kwargs": kwargs,
            "cmd": cmd,
            "flags": flags
        }
        return self.validate_command(command, validate_input=False)

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

    def validate_command(self, command, validate_input=True):
        if self.purge_at is not None and self.purge_at <= datetime.now():
            raise ValidationError("Resource is no longer valid and will get purged")
        # Internal asserts about the request
        assert isinstance(command, dict), \
            "Command should be a dictionary."
        assert isinstance(command["cmd"], list), \
            "Cmd should be a list that can be passed on to subprocess.run"
        if validate_input:
            self._validate_input(

                *command.get("args", tuple()),
                **command.get("kwargs", {})
            )
        # All is fine :)
        return command

    def clean_stdout(self, stdout):
        return stdout.decode("utf-8")

    def clean_stderr(self, stderr):
        return stderr.decode("utf-8")

    #######################################################
    # PROTECTED METHODS
    #######################################################
    # Some internal methods to execute the shell commands
    # Currently it wraps subprocess

    def _run(self):
        cmd = self.command.get("cmd")
        cwd = None
        env = self.environment(*self.command.get("args"), **self.command.get("kwargs"))
        if self.DIRECTORY_SETTING:
            cwd = getattr(datagrowth_settings, self.DIRECTORY_SETTING)
        results = subprocess.run(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=env
        )
        self._update_from_results(results)

    def _update_from_results(self, results):
        self.status = results.returncode
        self.stdout = self.clean_stdout(results.stdout)
        self.stderr = self.clean_stderr(results.stderr)

    def _handle_errors(self):
        if not self.success:
            class_name = self.__class__.__name__
            message = "{} > {} \n\n {}".format(class_name, self.status, self.stderr)
            raise DGShellError(message, resource=self)

    #######################################################
    # DJANGO MODEL
    #######################################################
    # Methods and properties to tweak Django

    def clean(self):
        if len(self.uri):
            self.uri = self.uri[:255]
        if not self.id and self.config.purge_immediately:
            self.purge_at = datetime.now()

    #######################################################
    # CONVENIENCE
    #######################################################
    # Some static methods to provide standardization

    @staticmethod
    def uri_from_cmd(cmd):
        cmd = copy(cmd)
        main = cmd.pop(0)
        cmd.sort()
        cmd.insert(0, main)
        return " ".join(cmd)

    class Meta:
        abstract = True
