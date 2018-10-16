from django.conf.urls import url

from core.views.community import CommunityView
from online_discourse.models import DiscourseSearchCommunity
from online_discourse.views import CreateDiscourseOrder, list_discourse_view


urlpatterns = [
    url(
        r'^discourse-search/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": DiscourseSearchCommunity},
        name=DiscourseSearchCommunity.get_name() + "_service"
    ),
    url(
        r'^discourse-search/order/?$',
        CreateDiscourseOrder.as_view(),
        name=DiscourseSearchCommunity.get_name() + "_order"
    ),
    url(
        r'^discourse-search/discourses/?$',
        list_discourse_view,
        name=DiscourseSearchCommunity.get_name() + "_list"
    ),
]
