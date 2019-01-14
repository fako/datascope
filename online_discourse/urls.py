from django.conf.urls import url
from rest_framework import routers

from core.views.community import CommunityView
from online_discourse.models import DiscourseSearchCommunity
from online_discourse.views import CreateDiscourseOrder, DiscourseViewSet


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
    )
]


router = routers.SimpleRouter()
router.register(
    'discourse-search/discourses',
    DiscourseViewSet,
    base_name=DiscourseSearchCommunity.get_name()
)
urlpatterns += router.urls
