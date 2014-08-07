import json

from HIF.input.http.core import JsonQueryLink, HttpQueryLink


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


class WikiDataItemLookup(JsonQueryLink):

    HIF_link = "http://en.wikipedia.org/w/api.php"
    HIF_parameters = {
        "action": "query",
        "format": "json",
        "prop": "pageprops",
        "ppprop": "wikibase_item",
    }

    HIF_query_parameter = "titles"

    HIF_objective = {
        "pageid": 0,
        "ns": None,
        "title": "",
        "pageprops.wikibase_item": ""
    }
    HIF_translations = {
        "pageprops.wikibase_item": "item"
    }

    class Meta:
        app_label = "HIF"
        proxy = True


# Throw away from here?
# TODO: It would be interesting to have a "raw" parser somehow.
#
# import re
#
# class WikiLondenDeath(JsonQueryLink):
#
#     HIF_link = "http://en.wikipedia.org/w/index.php"
#     HIF_parameters = {
#         "action": "raw",
#     }
#
#     HIF_query_parameter = "title"
#
#     @property
#     def data(self):
#         match = re.search(r'death_place\s*=\s*(?P<value>.*)',self.body)
#         if match:
#             possible_match = match.groups()[0]
#             if len(possible_match.strip(' ')) > 3:
#                 return possible_match
#             else:
#                 return ""
#         else:
#             return ""
#
#     class Meta:
#         app_label = "HIF"
#         proxy = True