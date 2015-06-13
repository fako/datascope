from itertools import groupby

from django.utils.translation import ugettext as _

from legacy.models.output import (VisualTranslationsStorage, PeopleSuggestionsStorage, CityCelebritiesStorage,
                                PopularityComparisonStorage)
from legacy.output.http.views import ProcessAPIView, ProcessPlainView, ServiceView
from legacy.output.http.handlers.warnings import handler_results_or_404, handler_wikipedia_disambiguation_300
from legacy.exceptions import HIFBadRequest, HIFNoInput


class Service(object):

    HIF_warning_handlers = []

    @property
    def name(self, word_separator='-'):
        class_name = self.__class__.__name__
        class_name = class_name.replace('Service', '')
        name = ''
        for index, char in enumerate(class_name):
            if char.isupper():
                name += word_separator + char.lower() if not index == 0 else char.lower()
            else:
                name += char
        return name

    def html_template(self, status):
        return '{}/{}'.format(self.name, status)

    def context(self, request):
        return {}

    def plain_view_preprocess(self, data):
        return data

    def handle_warnings(self, warnings, results):
        for handler in self.HIF_warning_handlers:
            for warning in warnings:
                handler(warning, results)


class VisualTranslationsService(VisualTranslationsStorage, Service):

    HIF_process = "VisualTranslations"

    HIF_main = ProcessAPIView
    HIF_plain = ProcessPlainView

    HIF_warning_handlers = [
        handler_results_or_404("WikiTranslate|404|message")
    ]

    class Meta:
        proxy = True

    def context(self, request):

        # Input validation
        query = request.GET.get('q', '').lower()
        media = request.GET.get('media', 'videos')
        if not query:
            raise HIFNoInput(_('No input provided'))
        if query and len(query.split(' ')) > 1:
            raise HIFBadRequest(_("We're sorry, we can't take more than one word as a query. Please try with one word at a time."))

        # Returning context
        return {
            "source_language": 'en',
            "query": query,
            "media": media
        }

    def plain_view_preprocess(self, data):
        langkey = lambda obj: obj["language"]
        data.sort(key=langkey)
        return [(lang, list(words),) for lang, words in groupby(data, langkey)]



class PeopleSuggestionsService(PeopleSuggestionsStorage, Service):

    HIF_process = "PeopleSuggestions"

    HIF_main = ProcessAPIView
    HIF_plain = ProcessPlainView

    HIF_warning_handlers = [
        handler_wikipedia_disambiguation_300("WikiSearch|300|message"),
        handler_results_or_404("WikiSearch|404|message"),
    ]

    class Meta:
        proxy = True

    def context(self, request):

        # Input validation
        query = request.GET.get('q', '')
        if not query:
            raise HIFNoInput(_('No input provided'))

        # Returning context
        return {
            "query": query
        }


class CityCelebritiesService(CityCelebritiesStorage, Service):

    HIF_main = ServiceView

    def context(self, request):
        return {
            "query": request.GET.get('q', '')
        }

    class Meta:
        proxy = True


class PopularityComparisonService(PopularityComparisonStorage, Service):

    HIF_process = "YouTubePopularityComparison"
    HIF_main = ProcessAPIView

    def context(self, request):
        return {
            "a": request.GET.get('a', ''),
            "b": request.GET.get('b', '')
        }

    class Meta:
        proxy = True