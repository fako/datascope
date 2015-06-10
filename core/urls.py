from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from wiki_news.models import WikiNewsCommunity
from . import views

urlpatterns = [
    url(r'^collective/(?P<pk>\d+)/content/$', views.CollectiveContentView.as_view()),
    url(r'^collective/(?P<pk>\d+)/$', views.CollectiveView.as_view()),
    url(r'^individual/(?P<pk>\d+)/content/$', views.IndividualContentView.as_view()),
    url(r'^individual/(?P<pk>\d+)/$', views.IndividualView.as_view()),
    url(r'^wiki-algo-news/$', views.CommunityView.as_view(), {"community_class": WikiNewsCommunity})
]