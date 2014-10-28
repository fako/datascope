from django.conf.urls import patterns, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from core.output.http.services.manifests import ImageTranslationsService, VideoTranslationsService, PeopleSuggestionsService

urlpatterns = patterns('core.views',
    url(r'^image-translations/$', ImageTranslationsService.HIF_main.as_view(), {"Service": ImageTranslationsService}, name='image-translations'),
    url(r'^image-translations/plain/$', ImageTranslationsService.HIF_plain.as_view(), {"Service": ImageTranslationsService}, name='image-translations-plain'),
    url(r'^video-translations/$', VideoTranslationsService.HIF_main.as_view(), {"Service": VideoTranslationsService}, name='video-translations'),
    url(r'^video-translations/plain/$', VideoTranslationsService.HIF_plain.as_view(), {"Service": VideoTranslationsService}, name='video-translations-plain'),

    url(r'^global-image-translations/plain/$', RedirectView.as_view(url=reverse_lazy('image-translations-plain'))),
    url(r'^global-video-translations/plain/$', RedirectView.as_view(url=reverse_lazy('video-translations-plain'))),

    url(r'^people-suggestions/$', PeopleSuggestionsService.HIF_main.as_view(), {"Service": PeopleSuggestionsService}, name='people-suggestions'),
    url(r'^people-suggestions/plain/$', PeopleSuggestionsService.HIF_plain.as_view(), {"Service": PeopleSuggestionsService}, name='people-suggestions-plain'),
)