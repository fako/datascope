from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from wiki_feed.urls import urlpatterns as wiki_feed_patterns
from visual_translations.urls import urlpatterns as visual_translations_patterns
from future_fashion.urls import urlpatterns as future_fashion_patterns
from topic_research.urls import urlpatterns as topic_research_patterns
from online_discourse.urls import urlpatterns as online_discourse_patterns
from . import views

urlpatterns = [
    url(r'^collective/(?P<pk>\d+)/content/$', views.CollectiveContentView.as_view(), name="collective-content"),
    url(r'^collective/(?P<pk>\d+)/$', views.CollectiveView.as_view(), name="collective"),
    url(r'^individual/(?P<pk>\d+)/content/$', views.IndividualContentView.as_view(), name="individual-content"),
    url(r'^individual/(?P<pk>\d+)/$', views.IndividualView.as_view(), name="individual"),
    url(r'^$', views.index, name="datascope-index"),
    url(r'^question/$', views.question, name="datascope-question")
]

urlpatterns += wiki_feed_patterns
urlpatterns += visual_translations_patterns
urlpatterns += future_fashion_patterns
urlpatterns += topic_research_patterns
urlpatterns += online_discourse_patterns
