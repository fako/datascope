from django.db import models


class HttpResource(models.Model):
    """
    A representation of how to fetch/submit data from/to a HTTP resource.
    Stores the headers and body for responses.
    """

    @classmethod
    def get(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: HttpResource
        """
        pass

    @classmethod
    def post(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: HttpResource
        """
        pass

    class Meta:
        abstract = True



input_schema = {
    "items": [{
        "type": "string",
        "pattern": "[A-Za-z0-9]+"  # a single alphanumeric
    }],
    "additionalItems": False
}