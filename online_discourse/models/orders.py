from django.db import models
from rest_framework import serializers


class DiscourseOrder(models.Model):

    name = models.CharField(max_length=255)
    email = models.EmailField()
    topic = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} ({})".format(self.topic, self.email)


class DiscourseOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiscourseOrder
        fields = "__all__"
