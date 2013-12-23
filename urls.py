from django.conf.urls import patterns, url

from HIF.output.http.services.manifests import ImageTranslationsService

urlpatterns = patterns('HIF.views',
    url(r'^image-translations/$', ImageTranslationsService.HIF_main.as_view(), {"Service": ImageTranslationsService}, name='image-translations'),
    url(r'^image-translations/plain/$', ImageTranslationsService.HIF_plain.as_view(), {"Service": ImageTranslationsService}, name='image-translations-plain'),
    #url(r'^image-translate/?$', 'portuguese_images', name='image-translate'),
    #url(r'^translate/?$', 'translate', name='translate'),
    #url(r'^image/?$', 'image', name='image'),
)