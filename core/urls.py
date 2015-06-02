from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^collective/(?P<pk>\d+)/content/$', views.CollectiveContentView.as_view()),
    url(r'^collective/(?P<pk>\d+)/$', views.CollectiveView.as_view())
]