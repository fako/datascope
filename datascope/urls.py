from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from . import views

urlpatterns = [
    url(r'', include('legacy.urls')),
    url(r'^data/v1/', include('core.urls', namespace="v1")),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^intersection/$', views.casting_comparison_by_face),
    url(r'^$', views.home)
]
