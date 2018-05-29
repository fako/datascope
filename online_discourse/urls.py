from django.conf.urls import url

from core.views.community import CommunityView
from online_discourse.models import DiscourseSearchCommunity
from online_discourse.views import SearchDumpCommunityView, CreateDiscourseOrder


urlpatterns = [
    url(
        r'^discourse-search/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": DiscourseSearchCommunity},
        name=DiscourseSearchCommunity.get_name() + "_service"
    ),
    url(
        r'^discourse-search/html/(?P<path>.+)?/?$',
        SearchDumpCommunityView.as_view(),
        kwargs={"community_class": DiscourseSearchCommunity},
        name=DiscourseSearchCommunity.get_name() + "_html"
    ),
    url(
        r'^discourse-search/order/?$',
        CreateDiscourseOrder.as_view(),
        name=DiscourseSearchCommunity.get_name() + "_order"
    ),
]
