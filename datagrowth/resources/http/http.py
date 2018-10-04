from urllib.parse import urlencode

import hashlib
import json
from copy import copy, deepcopy
from datetime import datetime

import requests
import jsonschema
from jsonschema.exceptions import ValidationError as SchemaValidationError
from urlobject import URLObject
from bs4 import BeautifulSoup

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

import json_field

from core.models.resources.resource import Resource
from core.exceptions import DSHttpError50X, DSHttpError40X


class HttpResource(Resource):
    # TODO: make sphinx friendly and doc all methods
    """
    A representation of how to fetch/submit data from/to a HTTP resource.

    Stores the headers, body and status of responses. It acts as a wrapper around requests library and provides:
    - responses from database when retrieved before
    - hooks to work with continuation URL's in responses
    - hooks to work with authentication
    """

    # Identification
    data_hash = models.CharField(max_length=255, db_index=True, default="")

    # Getting data
    request = json_field.JSONField(default=None)

    # Storing data
    head = json_field.JSONField(default="{}")
    body = models.TextField(default=None, null=True, blank=True)

    # Class constants that determine behavior
    URI_TEMPLATE = ""
    PARAMETERS = {}
    DATA = {}
    HEADERS = {}
    FILE_DATA_KEYS = []
    GET_SCHEMA = {
        "args": {},
        "kwargs": {}
    }
    POST_SCHEMA = {
        "args": {},
        "kwargs": {}
    }

    #######################################################
    # PUBLIC FUNCTIONALITY
    #######################################################
    # The get and post methods are the ways to interact
    # with the external resource.
    # Success and data are convenient to handle the results

    def send(self, method, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: HttpResource
        """
        if not self.request:
            self.request = self._create_request(method, *args, **kwargs)
            self.uri = HttpResource.uri_from_url(self.request.get("url"))
            self.data_hash = HttpResource.hash_from_data(
                self.request.get(HttpResource.get_data_key(self.request))
            )
        else:
            self.validate_request(self.request)

        self.clean()  # sets self.uri and self.data_hash based on request
        resource = None
        try:
            resource = self.__class__.objects.get(
                uri=self.uri,
                data_hash=self.data_hash
            )
            self.validate_request(resource.request)
        except (self.DoesNotExist, ValidationError):
            if resource is not None:
                resource.delete()
            resource = self

        if resource.success:
            return resource

        resource.request = resource.request_with_auth()
        resource._send()
        resource._handle_errors()
        return resource

    def get(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return self.send("get", *args, **kwargs)

    def post(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: HttpResource
        """
        return self.send("post", *args, **kwargs)

    @property
    def success(self):
        """
        Returns True if status is within HTTP success range
        """
        return self.status is not None and 200 <= self.status < 209

    @property
    def content(self):
        """

        :return: content_type, data
        """
        if self.success:
            content_type = self.head.get("content-type", "unknown/unknown").split(';')[0]
            if content_type == "application/json":
                return content_type, json.loads(self.body)
            elif content_type == "text/html":
                return content_type, BeautifulSoup(self.body, "html5lib")
            else:
                return content_type, None
        return None, None

    @property
    def meta(self):
        """

        :return: None
        """
        return None

    #######################################################
    # CREATE REQUEST
    #######################################################
    # A set of methods to create a request dictionary
    # The values inside are passed to the requests library
    # Override parameters method to set dynamic parameters

    def _create_request(self, method, *args, **kwargs):
        self._validate_input(method, *args, **kwargs)
        data = self.data(**kwargs) if not method == "get" else None
        headers = requests.utils.default_headers()
        headers["User-Agent"] = "{}; {}".format(self.config.user_agent, headers["User-Agent"])
        headers.update(self.headers())
        request = {
            "args": args,
            "kwargs": kwargs,
            "method": method,
            "url": self._create_url(*args),
            "headers": dict(headers)
        }
        data_key = self.get_data_key(request, headers)
        request[data_key] = data
        return self.validate_request(request, validate_input=False)

    def _create_url(self, *args):
        url_template = copy(self.URI_TEMPLATE)
        variables = self.variables(*args)
        url = URLObject(url_template.format(*variables["url"]))
        params = url.query.dict
        params.update(self.parameters(**variables))
        url = url.set_query_params(params)
        return str(url)

    def headers(self):
        """

        :return:
        """
        return self.HEADERS

    def parameters(self, **kwargs):
        """

        :return: dict
        """
        return self.PARAMETERS

    def data(self, **kwargs):
        """

        :return:
        """
        data = dict(self.DATA)
        data.update(**kwargs)
        return data

    def variables(self, *args):
        """

        :return:
        """
        return {
            "url": args
        }

    def create_request_from_url(self, url):
        raise NotImplementedError()

    def validate_request(self, request, validate_input=True):
        if self.purge_at is not None and self.purge_at <= datetime.now():
            raise ValidationError("Resource is no longer valid and will get purged")
        # Internal asserts about the request
        assert isinstance(request, dict), \
            "Request should be a dictionary."
        method = request.get("method")
        assert method, \
            "Method should not be falsy."
        assert method in ["get", "post"], \
            "{} is not a supported resource method.".format(request.get("method"))  # FEATURE: allow all methods
        if validate_input:
            self._validate_input(
                method,
                *request.get("args", tuple()),
                **request.get("kwargs", {})
            )
        # All is fine :)
        return request

    def _validate_input(self, method, *args, **kwargs):
        # Validations of external influence
        schemas = self.GET_SCHEMA if method == "get" else self.POST_SCHEMA  # FEATURE: allow all methods
        args_schema = schemas.get("args")
        kwargs_schema = schemas.get("kwargs")
        if args_schema is None and len(args):
            raise ValidationError("Received arguments for request where there should be none.")
        if kwargs_schema is None and len(kwargs):
            raise ValidationError("Received keyword arguments for request where there should be none.")
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

    def _format_data(self, data):
        if data is None:
            return None, None
        files = {}
        for file_key in self.FILE_DATA_KEYS:
            file_path = data.pop(file_key)
            files[file_key] = open(file_path, "rb")
        return data, files if files else None

    #######################################################
    # AUTH LOGIC
    #######################################################
    # Methods to enable auth for the resource.
    # Override auth_parameters to provide authentication.

    def auth_parameters(self):
        return {}

    def request_with_auth(self):
        url = URLObject(self.request.get("url"))
        params = url.query.dict
        params.update(self.auth_parameters())
        url = url.set_query_params(params)
        request = deepcopy(self.request)
        request["url"] = str(url)
        return request

    def request_without_auth(self):
        url = URLObject(self.request.get("url"))
        url = url.del_query_params(self.auth_parameters())
        request = deepcopy(self.request)
        request["url"] = str(url)
        return request

    #######################################################
    # NEXT LOGIC
    #######################################################
    # Methods to act on continuation for a resource
    # Override next_parameters to provide auto continuation

    def next_parameters(self):
        return {}

    def create_next_request(self):
        if not self.success or not self.next_parameters():
            return None
        url = URLObject(self.request.get("url"))
        params = url.query.dict
        params.update(self.next_parameters())
        url = url.set_query_params(params)
        request = deepcopy(self.request)
        request["url"] = str(url)
        return request

    #######################################################
    # PROTECTED METHODS
    #######################################################
    # Some internal methods for the get and post methods.

    def _send(self):
        """
        Does a get on the computed link
        Will set storage fields to returned values
        """
        assert self.request and isinstance(self.request, dict), \
            "Trying to make request before having a valid request dictionary."

        method = self.request.get("method")
        form_data = self.request.get("data") if not method == "get" else None
        form_data, files = self._format_data(form_data)
        json_data = self.request.get("json") if not method == "get" else None

        request = requests.Request(
            method=method,
            url=self.request.get("url"),
            headers=self.request.get("headers"),
            data=form_data,
            json=json_data,
            files=files
        )
        preq = self.session.prepare_request(request)

        try:
            response = self.session.send(
                preq,
                proxies=settings.REQUESTS_PROXIES,
                verify=settings.REQUESTS_VERIFY,
                timeout=self.timeout
            )
        except (requests.ConnectionError, IOError):
            self.set_error(502, connection_error=True)
            return
        except requests.Timeout:
            self.set_error(504, connection_error=True)
            return
        self._update_from_response(response)

    def _update_from_response(self, response):
        self.head = dict(response.headers.lower_items())
        self.status = response.status_code
        # TODO: check what to do with responses that contain invalid character bytes
        # TODO: check why sometimes we get strings and sometimes bytes in response.body
        self.body = response.content if isinstance(response.content, str) else \
            response.content.decode("utf-8", "replace")

    def _handle_errors(self):
        """
        Raises exceptions upon error statuses
        """
        class_name = self.__class__.__name__
        if self.status >= 500:
            message = "{} > {} \n\n {}".format(class_name, self.status, self.body)
            raise DSHttpError50X(message, resource=self)
        elif self.status >= 400:
            message = "{} > {} \n\n {}".format(class_name, self.status, self.body)
            raise DSHttpError40X(message, resource=self)
        else:
            return True

    #######################################################
    # DJANGO MODEL
    #######################################################
    # Methods and properties to tweak Django

    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop("session", requests.Session())
        self.timeout = kwargs.pop("timeout", 30)
        super(HttpResource, self).__init__(*args, **kwargs)

    def clean(self):
        if self.request and not self.uri:
            uri_request = self.request_without_auth()
            self.uri = HttpResource.uri_from_url(uri_request.get("url"))
        if self.request and not self.data_hash:
            uri_request = self.request_without_auth()
            self.data_hash = HttpResource.hash_from_data(uri_request.get("data"))
        if len(self.uri):
            self.uri = self.uri[:255]
        if not self.id and self.config.purge_immediately:
            self.purge_at = datetime.now()

    #######################################################
    # CONVENIENCE
    #######################################################
    # Some static methods to provide standardization

    @staticmethod
    def uri_from_url(url):
        url = URLObject(url)
        params = sorted(url.query.dict.items(), key=lambda item: item[0])
        url = url.with_query(urlencode(params))
        return str(url).replace(url.scheme + "://", "")

    @staticmethod
    def hash_from_data(data):
        if not data:
            return ""
        hsh = hashlib.sha1()
        hash_data = json.dumps(data).encode("utf-8")
        hsh.update(hash_data)
        return hsh.hexdigest()

    @staticmethod
    def get_data_key(request, headers=None):
        if "data" in request:
            return "data"
        elif "json" in request:
            return "json"
        elif headers:
            return "json" if headers.get("Content-Type") == "application/json" else "data"
        raise AssertionError("Could not determine data_key for request {} or headers {}".format(request, headers))

    def set_error(self, status, connection_error=False):
        if connection_error:
            self.head = {}
            self.body = ""
        self.status = status

    class Meta:
        abstract = True
