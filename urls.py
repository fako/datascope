from django.conf.urls import patterns, url

from HIF.output.http.services.manifests import ImageTranslationsService, VideoTranslationsService

urlpatterns = patterns('HIF.views',
    url(r'^image-translations/$', ImageTranslationsService.HIF_main.as_view(), {"Service": ImageTranslationsService}, name='image-translations'),
    url(r'^image-translations/plain/$', ImageTranslationsService.HIF_plain.as_view(), {"Service": ImageTranslationsService}, name='image-translations-plain'),
    url(r'^video-translations/$', VideoTranslationsService.HIF_main.as_view(), {"Service": VideoTranslationsService}, name='video-translations'),
    url(r'^video-translations/plain/$', VideoTranslationsService.HIF_plain.as_view(), {"Service": VideoTranslationsService}, name='video-translations-plain'),
)