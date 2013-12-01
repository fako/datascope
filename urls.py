from django.conf.urls import patterns, url

from HIF.output.http.views import ProcessView

urlpatterns = patterns('HIF.views',
    url(r'^image-translations/$', ProcessView.as_view(), {"name": "ImageTranslations"}, name='image-translations'),
    #url(r'^image-translate/?$', 'portuguese_images', name='image-translate'),
    #url(r'^translate/?$', 'translate', name='translate'),
    #url(r'^image/?$', 'image', name='image'),
)