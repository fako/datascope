from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^collective/(?P<pk>\d+)/$', views.CollectiveContentView.as_view())
]