from django.core.mail import mail_managers
from rest_framework import generics, throttling

from core.views.community import HtmlCommunityView
from online_discourse.models.orders import DiscourseOrderSerializer


class SearchDumpCommunityView(HtmlCommunityView):

    @staticmethod
    def data_for(community_class, response=None):
        data = HtmlCommunityView.data_for(community_class, response)
        if data is None:
            data = {}
        data["topics"] = {
            "immigration"
        }
        return data


class AnonDiscourseOrderThrottle(throttling.AnonRateThrottle):
    rate = "24/day"


class CreateDiscourseOrder(generics.CreateAPIView):
    serializer_class = DiscourseOrderSerializer
    throttle_classes = [AnonDiscourseOrderThrottle]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        mail_managers("discourse order!", "Please check the admin for order details")
        return response
