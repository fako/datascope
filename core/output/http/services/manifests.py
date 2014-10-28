from django.utils.translation import ugettext as _

from core.models.output import ImageTranslationsStorage, VideoTranslationsStorage, PeopleSuggestionsStorage
from core.output.http.views import ProcessAPIView, ProcessPlainView
from core.exceptions import HIFBadRequest, HIFNoInput


class Service(object):

    HIF_grid_layout = []

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


class ImageTranslationsService(ImageTranslationsStorage, Service):

    HIF_process = "ImageTranslations"

    HIF_main = ProcessAPIView
    HIF_plain = ProcessPlainView

    class Meta:
        proxy = True

    def context(self, request):

        # Input validation
        query = request.GET.get('q', '').lower()
        if not query:
            raise HIFNoInput(_('No input provided'))
        if query and len(query.split(' ')) > 1:
            raise HIFBadRequest(_("We're sorry, we can't take more than one word as a query. Please try with one word at a time."))

        # Returning context
        return {
            "source_language": 'en',
            "query": query
        }


class VideoTranslationsService(VideoTranslationsStorage, Service):

    HIF_process = "VideoTranslations"

    HIF_main = ProcessAPIView
    HIF_plain = ProcessPlainView

    class Meta:
        proxy = True

    def context(self, request):

        # Input validation
        query = request.GET.get('q', '').lower()
        if not query:
            raise HIFNoInput(_('No input provided'))
        if query and len(query.split(' ')) > 1:
            raise HIFBadRequest(_("We're sorry, we can't take more than one word as a query. Please try with one word at a time."))

        # Returning context
        return {
            "source_language": 'en',
            "query": query
        }


class PeopleSuggestionsService(PeopleSuggestionsStorage, Service):

    HIF_process = "PeopleSuggestions"

    HIF_main = ProcessAPIView
    HIF_plain = ProcessPlainView

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