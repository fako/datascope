import json

from core.utils.helpers import override_dict
from core.exceptions import DSInvalidResource, DSHttpError40X
from sources.models.wikipedia.base import WikipediaAPI


class WikipediaQuery(WikipediaAPI):

    URI_TEMPLATE = 'https://{}.wikipedia.org/w/api.php?{}={}'

    PARAMETERS = override_dict(WikipediaAPI.PARAMETERS, {
        "action": "query",
        "redirects": "1",
    })
    GET_SCHEMA = {
        "args": {},
        "kwargs": None
    }

    WIKI_RESULTS_KEY = "pages"
    WIKI_QUERY_PARAM = "titles"
    ERROR_MESSAGE = "We did not find the page you were looking for. Perhaps you should create it?"

    def send(self, method, *args, **kwargs):
        args = (self.config.wiki_country, self.WIKI_QUERY_PARAM,) + args
        return super(WikipediaQuery, self).send(method, *args, **kwargs)

    def _handle_errors(self):
        super(WikipediaQuery, self)._handle_errors()

        # Check general response
        content_type, data = self.content
        if "query" not in data:
            raise DSInvalidResource('Wrongly formatted Wikipedia response, missing "query"', resource=self)
        response = data['query'][self.WIKI_RESULTS_KEY]  # Wiki has response hidden under single keyed dicts :(

        # When searching for pages a dictionary gets returned
        # TODO: parse the dictionary and possibly return partial content
        if isinstance(response, dict) and "-1" in response and "missing" in response["-1"]:
            self.status = 404
            raise DSHttpError40X(self.ERROR_MESSAGE, resource=self)
        # When making lists a list is returned
        elif isinstance(response, list) and not response:
            self.status = 404
            raise DSHttpError40X(self.ERROR_MESSAGE, resource=self)

    @property
    def content(self):
        content_type, data = super(WikipediaQuery, self).content
        if "warnings" in data:
            del(data["warnings"])
        return content_type, data

    def get_wikipedia_json(self):
        # TODO: remove this method and its uses when a partial content is possible
        response = json.loads(self.body)
        return response["query"][self.WIKI_RESULTS_KEY]

    def next_parameters(self):
        content_type, data = self.content
        return data.get("continue", {})

    class Meta:
        abstract = True


class WikipediaGenerator(WikipediaQuery):

    def _handle_errors(self):
        """
        Generators have a habit of leaving out the query parameter if the query returns nothing :(
        :return:
        """
        try:
            super(WikipediaGenerator, self)._handle_errors()
        except DSInvalidResource:
            # This indicates the generator didn't find anything under the 'query' key in body
            # In practise it means the searched for title does not exist.
            self.status = 404
            raise DSHttpError40X(self.ERROR_MESSAGE, resource=self)

    class Meta:
        abstract = True


class WikipediaPage(WikipediaQuery):

    @property
    def content(self):
        """
        This class gets revisions for a single page. So we only return the revisions and not all page info.
        :return:
        """
        content_type, data = super(WikipediaQuery, self).content
        if data is None:
            return content_type, data
        try:
            page = next(iter(data["query"]["pages"].values()))
        except (KeyError, StopIteration, TypeError):
            raise DSInvalidResource(
                "{} resource did not contain 'query', 'pages' or a first page".format(self.__class__.__name__),
                resource=self
            )
        data["page"] = page
        return content_type, data

    class Meta:
        abstract = True
