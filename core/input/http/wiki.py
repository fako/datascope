# TODO: split up into separate files

import json

from core.input.http.base import JsonQueryLink, HttpJsonMixin, HttpLink
from core.input.helpers import sanitize_single_trueish_input
from core.exceptions import HIFUnexpectedInput, HIFHttpError40X, HIFHttpWarning300, HIFImproperUsage


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
        return super(WikiLocationSearch, self).prepare_next()

    class Meta:
        app_label = "core"
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
        link = super(WikiBaseQuery, self).prepare_link()
        return link.format(self.config.source_language)

    def handle_error(self):
        """
        Handles missing pages and ambiguity errors
        You can only handle these errors by parsing body :(
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
        app_label = "core"
        proxy = True


class WikiTranslate(WikiBaseQuery):

    HIF_link = 'http://{}.wiktionary.org/w/api.php'  # updated at runtime

    # TODO: Add a helper to do this and improve syntax looks?
    HIF_parameters = dict(WikiBaseQuery.HIF_parameters.copy(), **{
        'prop': 'info|pageprops|iwlinks',
        'iwprop': 'url',
        'iwprefix': None,  # set at runtime
    })

    HIF_objective = {
        "url": None,
        "*": None,
        "prefix": None
    }
    HIF_translations = {
        "*": "translation",
        "prefix": "language"
    }

    def prepare_params(self):
        """
        Prepare params sets the inter wiki prefix as a parameter depending on the language to translate to.
        """
        self.HIF_parameters['iwprefix'] = self.config.translate_to
        return super(WikiTranslate, self).prepare_params()

    class Meta:
        app_label = "core"
        proxy = True


class WikiDataClaims(HttpLink, HttpJsonMixin):

    HIF_link = "https://www.wikidata.org/wiki/Special:EntityData/{}.json"  # updated at runtime
    HIF_namespace = 'wiki'

    HIF_objective = {
        "property": "",
        "datavalue.value.numeric-id": 0
    }
    HIF_translations = {
        "datavalue.value.numeric-id": "item"
    }

    def __init__(self, *args, **kwargs):
        super(WikiDataClaims, self).__init__(*args, **kwargs)
        HttpJsonMixin.__init__(self)

    def sanitize_input(self, to_check):
        return sanitize_single_trueish_input(to_check, class_name=self.__class__.__name__)

    def prepare_link(self):
        link = super(WikiDataClaims, self).prepare_link()
        return link.format(self.input)

    def cleaner(self, result_instance):
        return result_instance['item'] and result_instance['property'] not in self.config.excluded_properties

    @property
    def rsl(self):
        return self.data

    class Meta:
        app_label = "core"
        proxy = True


class WikiDataClaimers(HttpLink, HttpJsonMixin):

    # TODO: add an exact operator to reach() to solve issue with similarly named keys

    HIF_link = "http://wdq.wmflabs.org/api?q={}"
    HIF_objective = {
        "status.items": 0,
        "items": []
    }

    def __init__(self, *args, **kwargs):
        super(WikiDataClaimers, self).__init__(*args, **kwargs)
        HttpJsonMixin.__init__(self)

    def sanitize_input(self, to_check):
        if not isinstance(to_check, (list, tuple,)):
            return False, "WikiDataClaimers is expects a list or tuple"
        # TODO write a sanitize function that checks for existence of keys
        for claim_input in to_check:
            if not "property" in claim_input or not "item" in claim_input:
                return False, "Found input without 'property' and 'item' keys: {}".format(to_check)
        return True, to_check

    def prepare_link(self):

        query_expression = "CLAIM[{}:{}] AND "
        query = ''
        for claim in self.input:
            property = claim['property'][1:]  # strips 'P'
            item = claim['item']
            query += query_expression.format(property, item)

        link = super(WikiDataClaimers, self).prepare_link()
        return link.format(query)[:-5]  # strips last AND

    @property
    def data(self):
        data = super(WikiDataClaimers, self).data
        return data[0]['items']

    @property  # TODO: how to implement these things correctly with mixins instead of having to add it all the time
    def rsl(self):
        return self.data

    class Meta:
        app_label = "core"
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
        app_label = "core"
        proxy = True