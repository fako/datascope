from django.db import models

import jsonfield

from core.fields import configuration
from core.configuration import DefaultConfiguration


class HttpResource(models.Model):
    """
    A representation of how to fetch/submit data from/to a HTTP resource.
    Stores the headers and body for responses.
    """
    uri = models.CharField(max_length=255, db_index=True, null=True)
    url = models.CharField(max_length=255, null=True)

    #head = jsonfield.JSONField()
    #body = jsonfield.JSONField()
    #status = models.PositiveIntegerField()

    input = jsonfield.JSONField(null=True)
    config = configuration.ConfigurationField(
        default_configuration=DefaultConfiguration(),
        default={}
    )

    GET_SCHEMA = {
        "args": {},
        "kwargs": {}
    }
    POST_SCHEMA = {
        "args": {},
        "kwargs": {}
    }
    URL_TEMPLATE = ""
    PARAMETERS = {}
    NEXT_PARAMETER = ""
    QUERY_PARAMETER = ""

    def get(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: HttpResource
        """
        pass

    def post(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: HttpResource
        """
        pass

    # class Meta:
    #     abstract = True



input_schema = {
    "items": [{
        "type": "string",
        "pattern": "[A-Za-z0-9]+"  # a single alphanumeric
    }],
    "additionalItems": False
}