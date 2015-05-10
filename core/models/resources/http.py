import requests
from copy import copy, deepcopy
from urlobject import URLObject

from django.db import models

import jsonfield

from core.exceptions import DSHttpError50X, DSHttpError40X
from core.utils import configuration
from core.configuration import DefaultConfiguration


class HttpResource(models.Model):
    """
    A representation of how to fetch/submit data from/to a HTTP resource.
    Stores the headers and body of responses.
    """

    # Identification
    uri = models.CharField(max_length=255, db_index=True)
    post_data = models.CharField(max_length=255, db_index=True, default="")

    # Getting data
    request = jsonfield.JSONField()
    config = configuration.ConfigurationField(default=DefaultConfiguration())

    # Storing data
    head = jsonfield.JSONField()
    body = models.TextField()
    status = models.PositiveIntegerField(default=0)

    # Archiving fields
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    purge_at = models.DateTimeField(null=True, blank=True)

    # Class constants that determine behavior
    GET_SCHEMA = {
        "args": {},
        "kwargs": {}
    }
    POST_SCHEMA = {
        "args": {},
        "kwargs": {}
    }
    URI_TEMPLATE = u""
    PARAMETERS = {}

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
            self.uri = self.request.get("url")
            self.post_data = hash(self.request.get("data"))
        else:
            self.validate_request(self.request)

        self.clean()  # sets self.uri and self.post_data based on request
        try:
            resource = self.objects.get(
                uri=self.uri,
                post_data=self.post_data
            )
        except self.DoesNotExist:
            resource = self

        if resource.success:
            return resource

        resource.request = resource.request_with_auth()
        resource._send_request()
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
        return self.status >= 200 and self.status < 207

    @property
    def data(self):
        """

        :return: content_type, data
        """
        return None, None

    #######################################################
    # CREATE REQUEST
    #######################################################
    # A set of methods to create a request dictionary
    # The values inside are passed to the requests library
    # Override parameters method to set dynamic parameters

    def _create_request(self, method, *args, **kwargs):
        return self.validate_request({
            "args": args,
            "kwargs": kwargs,
            "method": method,
            "url": self._create_url(*args),
            "headers": {},
            "data": kwargs,
        })

    def _create_url(self, *args):
        url_template = copy(unicode(self.URI_TEMPLATE))
        url = URLObject(url_template.format(*args))
        url.query.add_params(self.parameters())

    def parameters(self):
        return self.PARAMETERS

    def create_request_from_url(self, url):
        raise NotImplementedError()

    def validate_request(self, request):
        assert request.get("method"), \
            "Method should not be falsy."
        assert request.get("method") in ["get", "post"], \
            "{} is not a supported resource method.".format(request.get("method"))
        return request

    #######################################################
    # AUTH LOGIC
    #######################################################
    # Methods to enable auth for the resource.
    # Override auth_parameters to provide authentication.

    def auth_parameters(self):
        return {}

    def request_with_auth(self):
        url = URLObject(self.request.get("url"))
        url = url.query.add_params(self.auth_parameters())
        return deepcopy(self.request).set("url", url)

    def request_without_auth(self):
        url = URLObject(self.request.get("url"))
        url = url.query.delete_params(self.auth_parameters())
        return deepcopy(self.request).set("url", url)

    #######################################################
    # NEXT LOGIC
    #######################################################
    # Methods to act on continuation for a resource
    # Override next_parameters to provide auto continuation

    def next_parameters(self):
        return {}

    def create_next_request(self):
        url = URLObject(self.request.get("url"))
        url = url.query.add_params(self.next_parameters())
        return deepcopy(self.request).set("url", url)

    #######################################################
    # PROTECTED METHODS
    #######################################################
    # Some internal methods for the get and post methods.

    def _send_request(self):
        """
        Does a get on the computed link
        Will set storage fields to returned values
        """
        if self.session is None:
            connection = requests
        else:
            connection = self.session
        response = connection.get(self.url, headers=self.request_headers)

        self.head = dict(response.headers)
        self.body = response.content
        self.status = response.status_code

    def _handle_error(self):
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

    def __init__(self, session=None, *args, **kwargs):
        super(HttpResource, self).__init__(*args, **kwargs)
        self.session = session

    def clean(self):
        if self.request and not self.uri:
            uri_request = self.request_without_auth()
            self.uri = URLObject(uri_request.get("url"))
        if self.request and not self.post_data:
            uri_request = self.request_without_auth()
            self.post_data = hash(uri_request.get("data"))

    class Meta:
        abstract = True


class HttpResourceMock(HttpResource):

    def __init__(self, *args, **kwargs):
        super(HttpResourceMock, self).__init__(*args, **kwargs)
        self.session = None  # mock requests here

    def auth_parameters(self):
        return {"auth": 1}

    def next_parameters(self):
        return {"next": 1}


input_schema = {
    "items": [{
        "type": "string",
        "pattern": "[A-Za-z0-9]+"  # a single alphanumeric
    }],
    "additionalItems": False
}