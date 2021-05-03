from django.conf import settings
from django.conf.urls import url

from core.views import CommunityView, HtmlCommunityView
from core import views
from core.tests.mocks.community import CommunityMock


app_name = "core"
urlpatterns = [
    url(r'^collective/(?P<pk>\d+)/content/$', views.CollectiveContentView.as_view(), name="collective-content"),
    url(r'^collective/(?P<pk>\d+)/$', views.CollectiveView.as_view(), name="collective"),
    url(r'^individual/(?P<pk>\d+)/content/$', views.IndividualContentView.as_view(), name="individual-content"),
    url(r'^individual/(?P<pk>\d+)/$', views.IndividualView.as_view(), name="individual"),
]

if settings.USE_MOCKS:
    urlpatterns += [
        url(
            r'^mock/service/(?P<path>.+)?/?$',
            CommunityView.as_view(),
            kwargs={"community_class": CommunityMock},
            name=CommunityMock.get_name() + "_service"
        ),
        url(
            r'^mock/html/(?P<path>.+)?/?$',
            HtmlCommunityView.as_view(),
            kwargs={"community_class": CommunityMock},
            name=CommunityMock.get_name() + "_html"
        ),
    ]
