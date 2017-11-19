from django.conf.urls import url

from core.views import CommunityView, HtmlCommunityView
from .community import CommunityMock


urlpatterns = [
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
