from django.core.mail import mail_managers
from rest_framework import generics, throttling

from online_discourse.models.orders import DiscourseOrderSerializer


class AnonDiscourseOrderThrottle(throttling.AnonRateThrottle):
    rate = "24/day"


class CreateDiscourseOrder(generics.CreateAPIView):
    serializer_class = DiscourseOrderSerializer
    throttle_classes = [AnonDiscourseOrderThrottle]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        mail_managers("discourse order!", "Please check the admin for order details")
        return response
