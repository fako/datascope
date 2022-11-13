import os

from django.conf import settings
from django.db import models
from django.utils.html import format_html
from rest_framework import serializers

from .storage import Document


class ColorClothingSet(object):

    email = models.EmailField(null=True, blank=True)
    processing_permission = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    top_color = models.CharField(max_length=6)
    bottom_color = models.CharField(max_length=6)
    match_style = models.CharField(max_length=20, null=True, blank=True)

    #top_item = models.ForeignKey(Document, related_name="+", on_delete=models.DO_NOTHING)
    #bottom_item = models.ForeignKey(Document, related_name="+", on_delete=models.DO_NOTHING)

    def top_item_image(self):
        return format_html('<img width="100px" src="{}" /><div>{}</div',
            os.path.join(settings.MEDIA_URL, self.top_item["path"]),
            self.top_item["name"]
        )
    top_item_image.short_description = 'Top item'

    def bottom_item_image(self):
        return u'<img width="100px" src="{}" /><div>{}</div>'.format(
            os.sep + self.bottom_item["path"],
            self.bottom_item["name"]
        )
    bottom_item_image.short_description = 'Bottom item'
    bottom_item_image.allow_tags = True

    def top_item_name(self):
        return


class ColorClothingSetSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data.get("email", None) and not data.get("processing_permission", None):
            data["email"] = None
        return data

    class Meta:
        model = ColorClothingSet
        fields = "__all__"
