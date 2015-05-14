import hashlib
import json
from copy import copy, deepcopy

import requests
import jsonschema
from jsonschema.exceptions import ValidationError as SchemaValidationError
from urlobject import URLObject

from django.core.exceptions import ValidationError
from django.db import models

import jsonfield

from core.exceptions import DSHttpError50X, DSHttpError40X
from core.utils import configuration
from core.utils.mocks import MockRequests, MOCK_DEFAULTS


class HttpResource(models.Model):
    """
    A representation of how to fetch/submit data from/to a HTTP resource.
    Stores the headers and body of responses.
    """

    # Identification
    uri = models.CharField(max_length=255, db_index=True, default=None)
    post_data = models.CharField(max_length=255, db_index=True, default="")

    # Getting data
    request = jsonfield.JSONField(default=None)

    # Storing data
    head = jsonfield.JSONField(default=None)
    body = models.TextField(default=None)
    status = models.PositiveIntegerField(default=None)

    # Archiving fields
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    purge_at = models.DateTimeField(null=True, blank=True)

    # Class constants that determine behavior
    URI_TEMPLATE = u""
    PARAMETERS = {}
    HEADERS = {}
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

    def get(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: HttpResource
        """
        if not self.request:
            self.request = self._create_request("get", *args, **kwargs)
            self.uri = HttpResource.uri_from_url(self.request.get("url"))
            self.post_data = HttpResource.hash_from_data(
                self.request.get("data")
            )
        else:
            self.validate_request(self.request)

        self.clean()  # sets self.uri and self.post_data based on request
        try:
            resource = self.__class__.objects.get(
                uri=self.uri,
                post_data=self.post_data
            )
        except self.DoesNotExist:
            resource = self

        if resource.success:
            return resource

        resource.request = resource.request_with_auth()
        resource._make_request()
        resource._handle_errors()
        return resource

    def post(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: HttpResource
        """
        pass

    @property
    def success(self):
        """
        Returns True if status is within HTTP success range
        """
        return 200 <= self.status < 209

    @property
    def data(self):
        """

        :return: content_type, data
        """
        if self.success:
            content_type = self.head["Content-Type"].split(';')[0]
            if content_type == "application/json":
                return content_type, json.loads(self.body)
            else:
                return content_type, None
        return None, None

    #######################################################
    # CREATE REQUEST
    #######################################################
    # A set of methods to create a request dictionary
    # The values inside are passed to the requests library
    # Override parameters method to set dynamic parameters

    def _create_request(self, method, *args, **kwargs):
        self._validate_input(method, *args, **kwargs)
        return self.validate_request({
            "args": args,
            "kwargs": kwargs,
            "method": method,
            "url": self._create_url(*args),
            "headers": self.HEADERS,
            "data": kwargs,
        }, validate_input=False)

    def _create_url(self, *args):
        url_template = copy(unicode(self.URI_TEMPLATE))
        url = URLObject(url_template.format(*args))
        params = url.query.dict
        params.update(self.parameters())
        url.query.set_params(params)
        return unicode(url)

    def parameters(self):
        return self.PARAMETERS

    def create_request_from_url(self, url):
        raise NotImplementedError()

    def validate_request(self, request, validate_input=True):
        # Internal asserts about the request
        assert isinstance(request, dict), \
            "Request should be a dictionary."
        method = request.get("method")
        assert method, \
            "Method should not be falsy."
        assert method in ["get", "post"], \
            "{} is not a supported resource method.".format(request.get("method"))
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
        schemas = self.GET_SCHEMA if method == "get" else self.POST_SCHEMA
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
                raise ValidationError(ex)
        if kwargs_schema:
            try:
                jsonschema.validate(kwargs, kwargs_schema)
            except SchemaValidationError as ex:
                raise ValidationError(ex)

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
        request["url"] = unicode(url)
        return request

    def request_without_auth(self):
        url = URLObject(self.request.get("url"))
        url = url.del_query_params(self.auth_parameters())
        request = deepcopy(self.request)
        request["url"] = unicode(url)
        return request

    #######################################################
    # NEXT LOGIC
    #######################################################
    # Methods to act on continuation for a resource
    # Override next_parameters to provide auto continuation

    def next_parameters(self):
        return {}

    def create_next_request(self):
        url = URLObject(self.request.get("url"))
        params = url.query.dict
        params.update(self.next_parameters())
        url = url.set_query_params(params)
        request = deepcopy(self.request)
        request["url"] = unicode(url)
        return request

    #######################################################
    # PROTECTED METHODS
    #######################################################
    # Some internal methods for the get and post methods.

    def _make_request(self):
        """
        Does a get on the computed link
        Will set storage fields to returned values
        """
        assert self.request and isinstance(self.request, dict), \
            "Trying to make request before having a valid request dictionary."

        if self.session is None:
            connection = requests
        else:
            connection = self.session

        url = self.request.get("url")
        headers = self.request.get("headers")
        response = connection.get(url, headers=headers)

        self.head = dict(response.headers)
        self.body = response.content
        self.status = response.status_code

    def _handle_errors(self):
        """
        Raises exceptions upon error statuses
        """
        class_name = self.__class__.__name__
        if self.status >= 500:
            message = "{} > {} \n\n {}".format(class_name, self.status, self.body)
            raise DSHttpError50X(message)
        elif self.status >= 400:
            message = "{} > {} \n\n {}".format(class_name, self.status, self.body)
            raise DSHttpError40X(message)
        else:
            return True

    #######################################################
    # DJANGO MODEL
    #######################################################
    # Methods and properties to tweak Django

    def __init__(self, *args, **kwargs):
        super(HttpResource, self).__init__(*args, **kwargs)
        self.session = kwargs.get("session")

    def clean(self):
        if self.request and not self.uri:
            uri_request = self.request_without_auth()
            self.uri = HttpResource.uri_from_url(uri_request.get("url"))
        if self.request and not self.post_data:
            uri_request = self.request_without_auth()
            self.post_data = HttpResource.hash_from_data(uri_request.get("data"))

    #######################################################
    # CONVENIENCE
    #######################################################
    # Some static methods to provide standardization

    @staticmethod
    def uri_from_url(url):
        url = URLObject(url)
        return unicode(url).replace(url.scheme + u"://", u"")

    @staticmethod
    def hash_from_data(data):
        if not data:
            return ""
        hsh = hashlib.sha1()
        hsh.update(json.dumps(data))
        return hsh.hexdigest()

    class Meta:
        abstract = True


class HttpResourceMock(HttpResource):

    URI_TEMPLATE = "http://localhost:8000/{}/?q={}"
    PARAMETERS = {
        "param": 1
    }
    HEADERS = {
        "Accept": "application/json"
    }
    GET_SCHEMA = {
        "args": {
            "title": "resource mock arguments",
            "type": "array",  # a single alphanumeric element
            "items": [
                {
                    "type": "string",
                    "enum": ["en", "nl"]
                },
                {
                    "type": "string",
                    "pattern": "[A-Za-z0-9]+"
                }
            ],
            "additionalItems": False,
            "minItems": 2
        },
        "kwargs": None  # not allowed
    }
    POST_SCHEMA = {
        "args": {},
        "kwargs": {}
    }

    config = configuration.ConfigurationField(
        default=MOCK_DEFAULTS,
        namespace="mock"
    )

    def __init__(self, *args, **kwargs):
        super(HttpResourceMock, self).__init__(*args, **kwargs)
        self.session = MockRequests
        self.session.get.reset_mock()

    def get(self, *args, **kwargs):
        args = (self.config.source_language,) + args
        return super(HttpResourceMock, self).get(*args, **kwargs)

    def auth_parameters(self):
        return {
            "auth": 1,
            "key": self.config.secret
        }

    def next_parameters(self):
        content_type, data = self.data
        try:
            nxt = data.get("next")
        except (AttributeError, KeyError):
            return {}
        return {"next": nxt}
