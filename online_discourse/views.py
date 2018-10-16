from django.core.mail import mail_managers
from rest_framework import generics, throttling, viewsets
from rest_framework.response import Response

from online_discourse.models.orders import DiscourseOrderSerializer
from online_discourse.discourse import configurations, DiscourseConfiguration


class AnonDiscourseOrderThrottle(throttling.AnonRateThrottle):
    rate = "24/day"


class CreateDiscourseOrder(generics.CreateAPIView):
    serializer_class = DiscourseOrderSerializer
    throttle_classes = [AnonDiscourseOrderThrottle]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        mail_managers("discourse order!", "Please check the admin for order details")
        return response


class DiscourseViewSet(viewsets.ViewSet):

    def list(self, request):
        discourses = {
            name: discourse._asdict() for name, discourse in configurations.__dict__.items()
            if isinstance(discourse, DiscourseConfiguration)
        }
        return Response(discourses)

    def retrieve(self, request, pk=None):
        pass


list_discourse_view = DiscourseViewSet.as_view({"get": "list"})
