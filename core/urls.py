from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from wiki_news.urls import urlpatterns as wiki_news_patterns
from . import views

urlpatterns = [
    url(r'^collective/(?P<pk>\d+)/content/$', views.CollectiveContentView.as_view()),
    url(r'^collective/(?P<pk>\d+)/$', views.CollectiveView.as_view()),
    url(r'^individual/(?P<pk>\d+)/content/$', views.IndividualContentView.as_view()),
    url(r'^individual/(?P<pk>\d+)/$', views.IndividualView.as_view()),
]

urlpatterns += wiki_news_patterns
