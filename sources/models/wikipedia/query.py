from __future__ import unicode_literals, absolute_import, print_function, division

import hashlib

from core.models.resources.http import HttpResource
from core.exceptions import DSInvalidResource, DSHttpError40X


class WikipediaQuery(HttpResource):

    URI_TEMPLATE = 'http://{}.wikipedia.org/w/api.php?{}={}'
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8"
    }
    PARAMETERS = {
        "action": "query",
        "format": "json",
        "redirects": "1",
        "continue": ""
    }
    GET_SCHEMA = {
        "args": {},
        "kwargs": None
    }

    CONFIG_NAMESPACE = "wikipedia"
    WIKI_RESULTS_KEY = "pages"
    WIKI_QUERY_PARAM = "titles"

    def send(self, method, *args, **kwargs):
        args = (self.config.wiki_country, self.WIKI_QUERY_PARAM,) + args
        return super(WikipediaQuery, self).send(method, *args, **kwargs)

    def _handle_errors(self):
        """
        Handles missing pages and ambiguity errors
        You can only handle these errors by parsing the body :(
        """
        super(WikipediaQuery, self)._handle_errors()

        # Check general response
        content_type, data = self.content
        if "query" not in data:
            raise DSInvalidResource('Wrongly formatted Wikipedia response, missing "query"', resource=self)
        response = data['query'][self.WIKI_RESULTS_KEY]  # Wiki has response hidden under single keyed dicts :(

        # We force a 404 on missing pages
        message = "We did not find the page you were looking for. Perhaps you should create it?"
        # When searching for pages a dictionary gets returned
        if isinstance(response, dict) and "-1" in response and "missing" in response["-1"]:
            self.status = 404
            raise DSHttpError40X(message, resource=self)
        # When making lists a list is returned
        elif isinstance(response, list) and not response:
            self.status = 404
            raise DSHttpError40X(message, resource=self)

        return response

    @property
    def content(self):
        content_type, data = super(WikipediaQuery, self).content
        if "warnings" in data:
            del(data["warnings"])
        return content_type, data

    def next_parameters(self):
        content_type, data = self.content
        return data.get("continue", {})

    @staticmethod
    def get_wiki_image(file_name):
        md5 = hashlib.md5(file_name.encode("utf-8"))
        hexhash = md5.hexdigest()
        return 'http://upload.wikimedia.org/wikipedia/commons/{}/{}/{}'.format(
            hexhash[:1],
            hexhash[:2],
            file_name
        )

    class Meta:
        abstract = True