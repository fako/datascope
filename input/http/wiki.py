# TODO: split up into separate files

import json

from HIF.input.http.core import JsonQueryLink
from HIF.exceptions import HIFUnexpectedInput, HIFHttpError40X, HIFHttpWarning300


class WikiTranslate(JsonQueryLink):  # TODO: make this use the WikiBase

    HIF_link = 'http://{}.wiktionary.org/w/api.php' # updated at runtime
    HIF_parameters = {
        'format': 'json',
        'action': 'query',
        'prop': 'iwlinks',
        'iwurl': 1,
        'iwprefix': None,  # set at runtime
    }
    HIF_objective = {
        "url": None,
        "*": None,
    }
    HIF_translations = {
        "*": "translation"
    }
    HIF_query_parameter = 'titles'

    HIF_namespace = "wiki"

    def prepare_link(self):
        """
        Prepare link does some pre formatting by including the source_language as a sub domain.
        """
        self.HIF_link = self.HIF_link.format(self.config.source_language)
        return super(WikiTranslate, self).prepare_link()

    def prepare_params(self):
        """
        Prepare params sets the inter wiki prefix as a parameter depending on the language to translate to.
        """
        self.HIF_parameters['iwprefix'] = self.config.translate_to
        return super(WikiTranslate, self).prepare_params()

    class Meta:
        app_label = "HIF"
        proxy = True


##############################
# http://wikilocation.org
##############################


class WikiLocationSearch(JsonQueryLink):

    HIF_link = 'http://api.wikilocation.org/'
    HIF_parameters = {
        "type": "landmark",
        "radius": 10000,
    }

    HIF_objective = {
        "lat": 0.0,
        "lng": 0.0,
        "title": "",
        "url": "",
        "distance": ""
    }

    HIF_query_parameter = "coords"
    HIF_next_parameter = "offset"
    HIF_next_benchmark = 1  # TODO: weird, ask question about this

    def prepare_params(self):
        params = super(WikiLocationSearch, self).prepare_params()
        # We could filter out the coords parameter from params here
        # For now leaving it as a hack
        params += u"&lat={}&lng={}".format(*self.HIF_parameters["coords"].split('+'))
        return params

    def cleaner(self,result_instance):
        return not result_instance["title"].startswith('List')

    def prepare_next(self):
        data = json.loads(self.body)  # important to load "unclean" data for correct offset
        length = len(data["articles"])
        self.next_value = self.next_value + length if length else None
        super(WikiLocationSearch, self).prepare_next()

    class Meta:
        app_label = "HIF"
        proxy = True


##############################
# PROPER STYLE WIKI LINKS
##############################


class WikiBaseQuery(JsonQueryLink):

    HIF_link = 'http://{}.wikipedia.org/w/api.php'  # updated at runtime
    HIF_query_parameter = 'titles'
    HIF_namespace = "wiki"

    HIF_parameters = {
        "action": "query",
        "prop": "info|pageprops",  # we fetch a lot here and filter with objectives for simplicity sake
        "format": "json",
    }

    HIF_objective = {
        "pageid": 0,
        "ns": None,
        "title": "",
        "pageprops.wikibase_item": ""
    }
    HIF_translations = {
        "pageprops.wikibase_item": "wikidata"
    }

    def prepare_link(self):
        """
        Prepare link does some pre formatting by including the source_language as a sub domain.
        """
        self.HIF_link = self.HIF_link.format(self.config.source_language)
        return super(WikiBaseQuery, self).prepare_link()

    def handle_error(self):
        """
        Handles missing pages and ambiguity errors
        """
        super(WikiBaseQuery,self).handle_error()

        body = json.loads(self.body)
        # Check general response
        if "query" not in body or "pages" not in body['query']:
            raise HIFUnexpectedInput('Wrongly formatted Wikipedia response, missing "query" or "pages"')

        # We force a 404 on missing pages
        if "-1" in body["query"]["pages"] and "missing" in body["query"]["pages"]["-1"]:
            self.status = 404
            message = "{} > {} \n\n {}".format(self.type, self.status, self.body)
            raise HIFHttpError40X(message)

        # Look for ambiguity
        for page_id, page in body["query"]["pages"].iteritems():
            try:
                if "disambiguation" in page['pageprops']:
                    raise HIFHttpWarning300(page_id)
            except KeyError:
                raise HIFUnexpectedInput('Wrongly formatted Wikipedia response, missing "pageprops"')

    class Meta:
        proxy = True


class WikiSearch(WikiBaseQuery):

    @property
    def data(self):
        """
        When we use WikiSearch we expect a single item not a list
        So we take the first item from the list that data returns here
        """
        data = super(WikiSearch, self).data
        return data[0] if len(data) else {}

    class Meta:
        app_label = "HIF"
        proxy = True


# TODO: create a HttpLink generator for Wiki generators
class WikiBacklinks(JsonQueryLink):

    HIF_link = "http://en.wikipedia.org/w/api.php"
    HIF_parameters = {
        "action": "query",
        "generator": "backlinks",
        "prop": "info",
        "format": "json",
        "gbllimit": 500
    }

    HIF_query_parameter = "gbltitle"

    HIF_objective = {
        "pageid": 0,
        "ns": None,
        "title": ""
    }

    def cleaner(self,result_instance):

        if result_instance["title"].startswith('List'):
            return False
        elif result_instance["ns"] != 0:
            return False

        return True

    class Meta:
        app_label = "HIF"
        proxy = True